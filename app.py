from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
from resume_parser import parse_resume
from job_matcher import get_job_recommendations

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
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

        return render_template('result.html', data=parsed_data, recommendations=recommendations)
    return 'Invalid file type'

if __name__ == '__main__':
    app.run(debug=True)
