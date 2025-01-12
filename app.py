from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'innovation_is_key'

def get_db_connection():
    conn = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=database\SigmaElevators.accdb;')
    return conn

def is_valid_password(password):
    # Check if the password meets the criteria
    if len(password) < 8:
        return False
    if not any(char.isupper() for char in password):  # At least one uppercase letter
        return False
    if not any(char.isdigit() for char in password):  # At least one digit
        return False
    if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/~" for char in password):  # At least one special symbol
        return False
    return True

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Retrieve stored hashed password
            cursor.execute('SELECT Password FROM Users WHERE Email = ?', (email,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user[0], password):
                session['user_email'] = email
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid email or password. Please try again.", "error")
                return render_template('login.html')

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['re_password']

        if password != repassword:
            flash("Passwords do not match. Please try again.", "error")
            return render_template('signup.html')

        if not is_valid_password(password):
            flash("Password must be at least 8 characters long, include one uppercase letter, one number, and one special symbol.", "error")
            return render_template('signup.html')

        try:
            hashed_password = generate_password_hash(password)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Users (FirstName, LastName, Email, Password) VALUES (?, ?, ?, ?)', 
                           (first_name, last_name, email, hashed_password))
            conn.commit()
            conn.close()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return render_template('signup.html')

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        flash("Please log in to access the dashboard.", "error")
        return render_template("err405.html")
    return render_template('dashboard.html', email=session['user_email'])

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))

@app.route('/activity01_investment_strategies')
def activity01():
    if 'user_email' not in session:
        flash("Please log in to access the dashboard.", "error")
        return render_template("err405.html")
    return render_template('activity01_investment_strategies.html', email=session['user_email'])

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/finance_gpt')
def finance_gpt():
    return render_template('finance_gpt.html')

@app.route('/finance_gpt_download')
def finance_gpt_download():
    return render_template('finance_gpt_download.html')

@app.route('/gpt_android')
def gpt_android():
    try:
        return send_from_directory(directory='static/app_download', path='FinanceGPT.apk', as_attachment=True)
    except Exception as e:
        flash(f"An error occurred while trying to download the file: {str(e)}", "error")
        return redirect(url_for('finance_gpt_download'))
    
@app.route('/course_certificate_crash_course')
def course_certificate_crash_course():
    try:
        return send_from_directory(directory='static/images', path='CourseCompletionCertificate.png', as_attachment=True)
    except Exception as e:
        flash(f"An error occurred while trying to download the file: {str(e)}", "error")
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)