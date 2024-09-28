from flask import Flask, request, redirect, url_for, session, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import datetime

# Create the Flask app
app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Database setup - You can use either environment variable or hard-coded SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///morgan.db')
db = SQLAlchemy(app)

# Define the correct PIN for Morgan and Admin
correct_pin = '0215'
admin_pin = '4200'

# Patient Information
patient_name = "Morgan"
dob = "02/15/2001"

# Task list for daily check-ins
tasks = {
    "Monday": ["Feed the cat", "Take medication", "Take a break", "Short walk"],
    "Tuesday": ["Feed the cat", "Take medication", "Do light cleaning", "Take a break"],
    "Wednesday": ["Feed the cat", "Take medication", "Sit in the sun", "Relax"],
    "Thursday": ["Feed the cat", "Take medication", "Breathe deeply", "Plan the day"],
    "Friday": ["Feed the cat", "Take medication", "Take a break", "Journal thoughts"]
}

# Define the Task Log Model with added fields
class TaskLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(100))
    mood = db.Column(db.String(100))
    meds_taken = db.Column(db.String(100))
    tasks_completed = db.Column(db.String(500))
    anxiety_level = db.Column(db.String(100))  # New field for anxiety level
    stress_level = db.Column(db.String(100))   # New field for stress level
    notes = db.Column(db.Text)  # Additional notes Morgan can provide

# Initialize the database
with app.app_context():
    db.create_all()

# Route for the login page (PIN input)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pin = request.form['pin']
        if pin == correct_pin:
            session['logged_in'] = True
            session['user'] = 'morgan'
            return redirect(url_for('home'))
        elif pin == admin_pin:
            session['logged_in'] = True
            session['user'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error="Incorrect PIN. Please try again.")
    return render_template('login.html')

# Home page with daily prompts for Morgan
@app.route('/home')
def home():
    if not session.get('logged_in') or session.get('user') != 'morgan':
        return redirect(url_for('login'))
    
    today = datetime.datetime.now().strftime("%A")  # Get current day of the week
    daily_tasks = tasks.get(today, [])
    return render_template('index.html', name=patient_name, dob=dob, tasks=daily_tasks, today=today)

# Route to submit task completion (for Morgan)
@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('logged_in') or session.get('user') != 'morgan':
        return redirect(url_for('login'))
    
    completed_tasks = request.form.getlist('tasks')
    mood = request.form['mood']
    meds_taken = request.form['meds_taken']
    anxiety_level = request.form['anxiety_level']
    stress_level = request.form['stress_level']
    notes = request.form['notes']
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Save the log to the database
    new_log = TaskLog(
        date=today_date, mood=mood, meds_taken=meds_taken, tasks_completed=", ".join(completed_tasks),
        anxiety_level=anxiety_level, stress_level=stress_level, notes=notes
    )
    db.session.add(new_log)
    db.session.commit()

    return render_template('submitted.html', tasks=completed_tasks, mood=mood, meds_taken=meds_taken)

# Admin dashboard to view Morgan's progress
@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in') or session.get('user') != 'admin':
        return redirect(url_for('login'))

    logs = TaskLog.query.all()  # Fetch all logs from the database
    return render_template('admin_dashboard.html', logs=logs)

# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)