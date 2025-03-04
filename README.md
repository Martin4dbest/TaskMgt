# 🚀 Martinez Task Manager  

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)  
[![Flask](https://img.shields.io/badge/Flask-2.0+-orange.svg)](https://flask.palletsprojects.com/)  

Welcome to **Martinez Task Manager**, a simple and intuitive **task management system** built with Flask. It helps users **organize tasks**, **track progress**, and **boost productivity** with an elegant UI and seamless experience.

---

## 📌 Features  

✅ **User Authentication** (Signup, Login, Logout)  
✅ **Create, Read, Update & Delete (CRUD) Tasks**  
✅ **Task Prioritization & Deadlines**  
✅ **Responsive & Modern UI** (Bootstrap)  
✅ **Database Support (SQLite/PostgreSQL)**  
✅ **Secure Password Hashing**  
✅ **RESTful API Endpoints for Future Integration**  

---

## 🛠️ Tech Stack  

- **Frontend**: Bootstrap 5, HTML, CSS  
- **Backend**: Python, Flask  
- **Database**: SQLite (Can be upgraded to PostgreSQL)  
- **Authentication**: Flask-Login, Flask-WTF  
- **Deployment**: Gunicorn, Heroku (Optional)  

---

## 📂 Project Structure  

TaskMgt/ │── static/ # CSS, JS, Images │── templates/ # HTML Templates │── app.py # Main Flask Application │── models.py # Database Models │── forms.py # Flask-WTF Forms │── routes.py # Route Handlers │── config.py # Configuration Settings │── README.md # Project Documentation │── requirements.txt # Dependencies │── .gitignore # Git Ignore File │── LICENSE # License File


---

## 🚀 Installation & Setup  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/Martin4dbest/TaskMgt.git
cd TaskMgt

```


## 2️⃣ Create a Virtual Environment
python -m venv env
source env/bin/activate   # On macOS/Linux
env\Scripts\activate      # On Windows

## 3️⃣ Install Dependencies
pip install -r requirements.txt

## 4️⃣ Setup the Database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

## 5️⃣ Run the Flask App
flask run

Visit http://127.0.0.1:5000 in your browser.

## 🛠️ Usage Guide
Sign up for an account
Log in to access the dashboard
Create new tasks, set priorities, and deadlines
Mark tasks as completed when done
Edit or delete tasks as needed
Logout securely when finished


