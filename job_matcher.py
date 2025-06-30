import json

def get_job_recommendations(user_skills):
    with open('jobs.json', 'r') as f:
        jobs = json.load(f)

    recommended = []
    for job in jobs:
        match_score = len(set(job['skills']) & set(user_skills))
        if match_score > 0:
            recommended.append({
                'title': job['title'],
                'company': job['company'],
                'skills': job['skills'],
                'score': match_score
            })

    recommended.sort(key=lambda x: x['score'], reverse=True)
    return recommended[:3]
