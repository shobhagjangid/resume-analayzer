from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

from resume_parser import parse_resume
from job_matcher import get_job_recommendations

UPLOAD_FOLDER = 'uploads'
USER_DB_FILE = 'userdb.json'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- Utility Functions ----------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_users():
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'w') as f:
            json.dump({}, f)
    with open(USER_DB_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# ---------------- Routes ----------------
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html', user=session['user'])

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = ''
    success = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username in users:
            message = 'User already exists. Try a different username.'
        else:
            users[username] = {
                'password': generate_password_hash(password)
            }
            save_users(users)
            message = 'Signup successful! You can now log in.'
            success = True
    return render_template('signup.html', message=message, success=success)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users and check_password_hash(users[username]['password'], password):
            session['user'] = username
            return redirect('/')
        else:
            message = 'Invalid credentials. Please try again.'
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user' not in session:
        return redirect('/login')

    if 'resume' not in request.files:
        return 'No file part'
    file = request.files['resume']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        parsed_data = parse_resume(filepath)
        recommendations = get_job_recommendations(parsed_data['skills'])

        return render_template('result.html', data=parsed_data, recommendations=recommendations, user=session.get('user'))
    return 'Invalid file type'

# ---------------- Run ----------------
if __name__ == '__main__':
    if not os.path.exists(USER_DB_FILE):
        save_users({})
    app.run(debug=True)
