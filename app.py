from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from datetime import date, timedelta
from sqlalchemy import func
from flask import flash  # Make sure you imported flash if you want to show errors
import csv
from flask import Response, session
import os
from sqlalchemy import extract
from collections import defaultdict
from flask_login import UserMixin
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# Expense Tracker Application
# This application allows users to track their expenses, filter by category, and view expenses within a specified date range.   

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'myexp') # for FLASK_SECRET_KEY, use an environment variable for production
# Set up the database
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.sqlite3'
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    def __repr__(self):
            return f'<{self.id, self.username}>'
    
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    note = db.Column(db.String(100))
    date = db.Column(db.Date, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Init
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # redirect if not logged in

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

bcrypt = Bcrypt(app)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            remember = 'remember' in request.form
            login_user(user, remember=remember)
            return redirect(url_for('index'))
    return render_template('login.html')

from datetime import timedelta

app.permanent_session_lifetime = timedelta(minutes=30)  # auto logout after 30 mins

@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    from datetime import date, datetime, timedelta
    categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping', 'Other']

    # Check for quick filter
    quick = request.args.get('quick')
    today = date.today()

    if quick == 'last7':
        from_date = today - timedelta(days=6)  # Includes today
        to_date = today
    elif quick == 'thismonth':
        from_date = today.replace(day=1)
        to_date = today
    else:
        # Get from form
        from_date_str = request.args.get('from_date')
        to_date_str = request.args.get('to_date')

        default_from = today - timedelta(days=30)
        default_to = today

        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else default_from
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else default_to

            if from_date > to_date:
                flash("⚠️ 'From Date' must be earlier than 'To Date'. Showing last 30 days.")
                from_date, to_date = default_from, default_to
        except Exception:
            flash("⚠️ Invalid date. Showing last 30 days.")
            from_date, to_date = default_from, default_to

    selected_filter = request.args.get('filter')
    expenses = Expense.query.filter_by(user_id=current_user.id)

    if selected_filter:
        expenses = expenses.filter_by(category=selected_filter)

    expenses = expenses.filter(Expense.date >= from_date, Expense.date <= to_date)
    expenses = expenses.order_by(Expense.date.desc()).all()
    total_amount = sum(e.amount for e in expenses )
    dur = (to_date - from_date).days + 1  # Include both start and end dates
    average_amount = total_amount /  dur if expenses else 0

    return render_template('index.html',
                           expenses=expenses,
                           categories=categories,
                           filter=selected_filter,
                           from_date=from_date,
                           to_date=to_date, 
                           total_amount=total_amount, 
                           average_amount=average_amount)




@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    
    categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping', 'Others']
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        note = request.form['note']
        expense = Expense(amount=amount, category=category, note=note, user_id=current_user.id)
        db.session.add(expense)
        db.session.commit()
        return redirect('/')
    return render_template('add.html', categories=categories)

@app.route('/export')
@login_required
def export_csv():
    from datetime import datetime
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    selected_filter = request.args.get('filter')

    query = Expense.query.filter_by(user_id=current_user.id)

    # Apply filters
    if selected_filter:
        query = query.filter_by(category=selected_filter)

    if from_date:
        query = query.filter(Expense.date >= datetime.strptime(from_date, '%Y-%m-%d').date())
    if to_date:
        query = query.filter(Expense.date <= datetime.strptime(to_date, '%Y-%m-%d').date())

    expenses = query.order_by(Expense.date.desc()).all()

    # Create CSV response
    def generate():
        data = [['Date', 'Category', 'Amount', 'Note', 'user_id']]
        for e in expenses:
            data.append([e.date.strftime('%Y-%m-%d'), e.category, e.amount, e.note or '', e.user_id])
        output = csv.StringIO()
        writer = csv.writer(output)
        writer.writerows(data)
        return output.getvalue()

    return Response(generate(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=expenses.csv'})



@app.route('/import', methods=['POST'])
@login_required
def import_csv():
    import io
    file = request.files['file']

    if not file or not file.filename.endswith('.csv'):
        flash('Please upload a valid CSV file.', 'warning')
        return redirect(url_for('index'))

    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.DictReader(stream)

    count = 0
    for row in reader:
        try:
            new_expense = Expense(
                date=datetime.strptime(row['Date'], '%d-%m-%Y').date(),
                category=row['Category'],
                amount=float(row['Amount']),
                note=row.get('Note', ''),
                user_id=current_user.id  # Associate with the logged-in user
            )
            db.session.add(new_expense)
            count += 1
        except Exception as e:
            print(f"Skipping row due to error: {e}")
            continue

    db.session.commit()
    flash(f'Imported {count} expenses from CSV.', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    expense = Expense.query.get_or_404(id, user_id=current_user.id)  # Ensure the expense belongs to the logged-in user
    categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping', 'Others']

    if request.method == 'POST':
        expense.amount = float(request.form['amount'])
        expense.category = request.form['category']
        expense.note = request.form['note']
        db.session.commit()
        flash('Expense updated successfully!')
        return redirect('/')

    return render_template('edit.html', expense=expense, categories=categories)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    expense = Expense.query.get_or_404(id, user_id=current_user.id)  # Ensure the expense belongs to the logged-in user
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!')
    return redirect('/')

@app.route('/analytics')
@login_required
def analytics():

    # Get filters from request
    from_date_str = request.args.get('from_date')
    to_date_str = request.args.get('to_date')
    selected_category = request.args.get('category')
    group_by = request.args.get('group_by', 'monthly')  # 'daily' or 'weekly'


    # Defaults
    today = date.today()
    default_from = today - timedelta(days=90) # default to 90 days ago

    # Parse dates or use defaults
    try:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else default_from
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else today
    except ValueError:
        from_date, to_date = default_from, today

    # Build the base query
    query = db.session.query(
        Expense.category,
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == current_user.id,  # Ensure the expense belongs to the logged-in user
        Expense.date >= from_date,
        Expense.date <= to_date
    )
    if selected_category and selected_category != 'All':
        query = query.filter(Expense.category == selected_category)

    query = query.group_by(Expense.category).all()

    chart_labels = [row[0] for row in query]
    chart_data = [float(row[1]) for row in query]

    # For the dropdown
    categories = ['All'] + sorted({e.category for e in Expense.query.with_entities(Expense.category).distinct()})

    
    # Daily totals for the selected date range
    daily_totals = db.session.query(
        Expense.date,
        func.sum(Expense.amount)
    ).filter(
        Expense.date >= from_date,
        Expense.date <= to_date,
        Expense.user_id == current_user.id  # Ensure the expense belongs to the logged-in user
    )

    if selected_category and selected_category != 'All':
        daily_totals = daily_totals.filter(Expense.category == selected_category)

    daily_totals = daily_totals.group_by(Expense.date).order_by(Expense.date).all()

    bar_labels = [d[0].strftime('%Y-%m-%d') for d in daily_totals]
    bar_data = [float(d[1]) for d in daily_totals]
    total_amount = sum(bar_data)
    dur = (to_date - from_date).days + 1
    # Calculate average amount
    average_amount = total_amount / dur if bar_data else 0

    # add weekly or daily trend
    # Get all expenses for date range
    expenses = db.session.query(
        Expense.date,
        Expense.amount
    ).filter(
        Expense.date >= from_date,
        Expense.date <= to_date, 
        Expense.user_id == current_user.id  # Ensure the expense belongs to the logged-in user
    )

    if selected_category and selected_category != 'All':
        expenses = expenses.filter(Expense.category == selected_category)

    expenses = expenses.all()
    
    time_grouped = defaultdict(float)

    for exp_date, amount in expenses:
        if group_by == 'weekly':
            year, week, _ = exp_date.isocalendar()
            key = f"{year}-W{week:02d}"  # Example: "2024-W23"
        else:
            key = exp_date.strftime('%Y-%m')  # Monthly

        time_grouped[key] += float(amount)

    # Sort results
    time_labels = sorted(time_grouped.keys())
    if group_by == "weekly":
        readable_labels = time_labels
    else:
        readable_labels = [datetime.strptime(label, '%Y-%m').strftime('%b %Y') for label in time_labels]

    time_data = [time_grouped[label] for label in time_labels]

    
    return render_template('analytics.html',
                    chart_labels=chart_labels,
                    chart_data=chart_data,
                    bar_labels=bar_labels,
                    bar_data=bar_data,
                    from_date=from_date.strftime('%Y-%m-%d'),
                    to_date=to_date.strftime('%Y-%m-%d'),
                    selected_category=selected_category or 'All',
                    categories=categories,
                    total_amount=total_amount,
                    average_amount=average_amount,
                    time_labels=readable_labels,
                    time_data=time_data,
                    group_by=group_by)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)