import re
import os
import PyPDF2
from flask import Flask, render_template, request

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SKILLS = [
    "python", "java", "c++", "machine learning", "deep learning", "api",
    "data analysis", "sql", "nosql", "aws", "azure", "docker", "kubernetes",
    "linux", "git", "rest", "django", "flask", "html", "css", "javascript"
]

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text.lower()

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().lower()

def clean_text(text):
    return re.sub(r"[^a-z0-9+\s]", " ", text)

def skill_present(skill, text):
    if " " in skill:
        return skill in text
    return re.search(rf"\b{re.escape(skill)}\b", text) is not None

def find_missing_skills(resume_text, job_text):
    return [
        skill for skill in SKILLS
        if skill_present(skill, job_text) and not skill_present(skill, resume_text)
    ]


@app.route("/", methods=["GET", "POST"])
def index():
    missing_skills = []
    if request.method == "POST":
        resume = request.files["resume"]
        job_desc = request.files["job"]

        resume_path = os.path.join(UPLOAD_FOLDER, resume.filename)
        job_path = os.path.join(UPLOAD_FOLDER, job_desc.filename)

        resume.save(resume_path)
        job_desc.save(job_path)

        resume_text = clean_text(extract_text_from_pdf(resume_path))
        job_text = clean_text(extract_text_from_txt(job_path))

        missing_skills = find_missing_skills(resume_text, job_text)

    return render_template("index.html", missing_skills=missing_skills)

if __name__ == "__main__":
    app.run(debug=True)
