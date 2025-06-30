import os
import json
import re
from pdfminer.high_level import extract_text
import docx2txt

def extract_email(text):
    # Corrected regex for valid email
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else "Not found"

def extract_name(text):
    lines = text.split("\n")
    for line in lines[:10]:
        line = line.strip()
        if line and line[0].isupper() and len(line.split()) <= 4:
            if not any(char in line for char in "@0123456789:"):
                return line
    return "Detected Candidate"

def parse_resume(file_path):
    text = ""
    if file_path.endswith('.pdf'):
        text = extract_text(file_path)
    elif file_path.endswith('.docx'):
        text = docx2txt.process(file_path)

    skills_keywords = ['python', 'java', 'sql', 'flask', 'django', 'excel', 'html', 'css', 'js', 'react', 'spring', 'Sql']
    found_skills = [skill for skill in skills_keywords if skill.lower() in text.lower()]

    return {
        'name': extract_name(text),
        'email': extract_email(text),
        'skills': found_skills,
        'text_snippet': text[:500]
    }

def get_job_recommendations(user_skills):
    with open('jobs.json', 'r') as f:
        jobs = json.load(f)

    recommended = []
    for job in jobs:
        job_skills = [skill.lower() for skill in job['skills']]
        match_count = len(set(job_skills) & set([s.lower() for s in user_skills]))
        score = int((match_count / len(job_skills)) * 100) if job_skills else 0

        if match_count > 0:
            recommended.append({
                'title': job['title'],
                'company': job['company'],
                'skills': job['skills'],
                'score': score
            })

    recommended.sort(key=lambda x: x['score'], reverse=True)
    return recommended[:3]
