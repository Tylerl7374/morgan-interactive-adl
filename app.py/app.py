from flask import Flask, render_template, request, redirect, url_for, session
import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # You can generate a stronger key

# Define the required PIN
correct_pin = '0215'

# Patient Information
patient_name = "Morgan"
dob = "02/15/2000"

# Task list for daily check-ins
tasks = {
    "Monday": ["Take medication", "Exercise", "Eat a balanced meal", "Complete morning routine"],
    "Tuesday": ["Take medication", "Read a book", "Talk to a friend", "Complete evening routine"],
    "Wednesday": ["Take medication", "Go for a walk", "Relax", "Journal thoughts"],
    "Thursday": ["Take medication", "Practice self-care", "Plan the weekend", "Clean the house"],
    "Friday": ["Take medication", "Prepare for next week", "Enjoy free time", "Complete week wrap-up"]
}

# Route for the login page (PIN input)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pin = request.form['pin']
        if pin == correct_pin:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Incorrect PIN. Please try again.")
    return render_template('login.html')

# Home page with daily prompts (after successful login)
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    today = datetime.datetime.now().strftime("%A")  # Get current day of the week
    daily_tasks = tasks.get(today, [])
    return render_template('index.html', name=patient_name, dob=dob, tasks=daily_tasks, today=today)

# Route to submit task completion
@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    completed_tasks = request.form.getlist('tasks')
    mood = request.form['mood']
    meds_taken = request.form['meds_taken']
    # Store the information in a database or a file for your records
    return render_template('submitted.html', tasks=completed_tasks, mood=mood, meds_taken=meds_taken)

# Logout route to clear session and return to login
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)