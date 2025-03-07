import os
import boto3
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileAllowed
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Flask Configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'

# AWS S3 Configuration
app.config['S3_BUCKET'] = os.getenv("AWS_S3_BUCKET")
app.config['S3_REGION'] = os.getenv("AWS_S3_REGION", "us-east-1")
app.config['AWS_ACCESS_KEY_ID'] = os.getenv("AWS_ACCESS_KEY_ID")
app.config['AWS_SECRET_ACCESS_KEY'] = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initialize S3 Client
s3 = boto3.client(
    "s3",
    aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
    region_name=app.config['S3_REGION']
)

# Database & Migrations
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_pic = db.Column(db.String(255), nullable=True)



    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy='dynamic'))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Forms
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Add Task')

class ProfileUpdateForm(FlaskForm):
    profile_pic = FileField("Update Profile Picture", validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], "Images only!")])
    submit = SubmitField("Update")

# Upload to S3
def upload_file_to_s3(file, bucket_name, folder="profile_pics"):
    filename = secure_filename(file.filename)
    s3_key = f"{folder}/{filename}"
    s3.upload_fileobj(file, bucket_name, s3_key)
    return f"https://{bucket_name}.s3.{app.config['S3_REGION']}.amazonaws.com/{s3_key}"

@app.route('/upload_profile_pic', methods=['POST'])
@login_required
def upload_profile_pic():
    if 'profile_pic' not in request.files or request.files['profile_pic'].filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('dashboard'))

    file = request.files['profile_pic']
    file_url = upload_file_to_s3(file, app.config['S3_BUCKET'], folder="profile_pics")

    if file_url:
        current_user.profile_pic = file_url
        db.session.commit()
        flash('Profile picture updated!', 'success')

    return redirect(url_for('dashboard'))



# Routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login'))
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', tasks=tasks, user=current_user)



@app.route("/add-task", methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('task.html', form=form)


@app.route('/delete_task/<int:task_id>', methods=['POST', 'GET'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    else:
        flash('Task not found!', 'danger')
    return redirect(url_for('dashboard'))


@app.route('/complete_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = True
        db.session.commit()
    return redirect(url_for('dashboard'))


@app.route("/tasks")
@login_required
def tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', tasks=tasks, user=current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

"""
if __name__ == "__main__":
    app.run(debug=True)

"""