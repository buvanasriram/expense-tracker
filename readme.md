# 💰 Expense Tracker Web Application

## 🧩 Overview
The **Expense Tracker** is a web-based application built using **Flask** that allows users to manage their personal finances effectively.  
It includes secure authentication, expense tracking, filtering, CSV import/export, and visual analytics.

---

## ⚙️ Features
| Feature | Description |
|----------|--------------|
| 🔐 **User Authentication** | Register, login, and logout with hashed passwords using Flask-Login and Flask-Bcrypt. |
| 💾 **Expense Management** | Add, edit, delete, and list expenses easily. |
| 🔎 **Filtering** | Filter expenses by date, category, or period (e.g., last 7 days, this month). |
| 📊 **Analytics Dashboard** | Category-wise and date-wise charts with recurring expense detection. |
| 📁 **CSV Export/Import** | Export filtered expenses or import data from a CSV file. |
| ⏳ **Auto Logout** | Session expires automatically after 30 minutes of inactivity. |

---

## 🏗️ Project Structure
ExpenseTracker/
│
├── app.py                  # Main Flask app
├── expenses.sqlite3        # SQLite database
├── templates/              # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── index.html
│   ├── add.html
│   ├── edit.html
│   └── analytics.html
└── static/                 # Optional: CSS, JS, images

---

## 🧰 Tech Stack
| Layer | Technology |
|-------|-------------|
| **Backend** | Python, Flask |
| **Database** | SQLite (via SQLAlchemy ORM) |
| **Authentication** | Flask-Login, Flask-Bcrypt |
| **Frontend** | HTML + Jinja2 Templates |
| **Charts** | Chart.js or Plotly (on analytics page) |

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/expense-tracker-flask.git
cd expense-tracker-flask

2️⃣ Create a Virtual Environment
python -m venv venv
.\venv\Scripts\activate    # Windows
# or
source venv/bin/activate   # Mac/Linux

3️⃣ Install Dependencies
pip install flask flask_sqlalchemy flask_login flask_bcrypt

4️⃣ Run the Application
python app.py

Open your browser and visit:
http://127.0.0.1:5000/


🧱 Database Models
🧍 User
FieldTypeDescriptionidInteger (PK)Unique user IDusernameString(150)Unique usernamepasswordString(200)Hashed password
💸 Expense
FieldTypeDescriptionidInteger (PK)Expense IDamountFloatExpense amountcategoryString(50)Expense categorynoteString(100)Optional notesdateDateExpense dateuser_idForeignKey(User.id)Linked user

🌐 Main Routes
RouteMethodDescription/registerGET, POSTUser registration/loginGET, POSTUser login/logoutGETLogout user/GETDashboard with expenses/addGET, POSTAdd new expense/edit/<id>GET, POSTEdit an expense/delete/<id>GETDelete expense/exportGETExport expenses to CSV/importPOSTImport expenses from CSV/analyticsGETView analytics dashboard

📊 Analytics Features
The Analytics Dashboard (/analytics) displays:


Category-wise totals — Pie chart view


Date-wise spending trends — Bar/Line chart


Recurring expense detection — Categories with monthly-like frequency (25–35 days apart)



🔐 Security


Passwords are hashed using Flask-Bcrypt


Session timeout after 30 minutes (app.permanent_session_lifetime)


Authentication required for all expense routes (@login_required)


Configurable FLASK_SECRET_KEY for added security



📤 CSV Import/Export
Export
Export all or filtered expenses as CSV:
GET /export

Import
Upload a CSV file in this format:
Date, Category, Amount, Note

(Date format: DD-MM-YYYY)

💡 Recurring Expense Detection
The app checks for recurring patterns by analyzing time gaps between expenses in the same category.
If at least two gaps fall between 25–35 days, the category is flagged as recurring.

🧾 Example Screens (Showcase Ideas)
Include screenshots or short demo videos of:


🧍 Login & Registration page


🏠 Dashboard with expense list


➕ Add/Edit expense forms


📊 Analytics page with charts


📁 CSV Import/Export dialogs



🚀 Deployment (Optional)
Hosting Options
You can deploy the app for free on:


Render


Railway


PythonAnywhere


Steps


Create a requirements.txt:
pip freeze > requirements.txt



Push code to GitHub.


Deploy on any platform and get a live URL, e.g.:
https://your-app-name.onrender.com




🌱 Future Enhancements


🎯 Budget goal setting & alerts


🧾 Monthly summary reports


☁️ Cloud database (PostgreSQL/Firebase)


📱 REST API for mobile integration


👥 Multi-user collaboration



👨‍💻 Author
Your Name
📧 [buvana.sriram@gmail.com]
🌐 [www.linkedin.com/in/buvana-swaminathan-73063b6]

🏁 License
This project is licensed under the MIT License.
Feel free to use and modify it for personal or educational purposes.

