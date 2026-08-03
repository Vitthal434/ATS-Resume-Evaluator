from flask import Flask, render_template, request
from flask import send_file

from resume_parser import read_pdf, read_docx, clean_text
from matcher import final_match_score
from job_recommender import recommend_jobs
from report_generator import generate_report

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/match", methods=["POST"])
def match():
    resume = request.files["resume"]
    job_desc = request.form["job_description"]

    # Extract text from the uploaded resume.
    if resume.filename.endswith(".pdf"):
        resume_text = read_pdf(resume)
    else:
        resume_text = read_docx(resume)

    # Normalize resume and job description text before matching.
    resume_text = clean_text(resume_text)
    job_desc = clean_text(job_desc)

    # Generate the ATS result, job recommendations, and downloadable report.
    result = final_match_score(resume_text, job_desc)
    matched_skills = result["matched_skills"]
    recommended_jobs = recommend_jobs(matched_skills)

    pdf_path = generate_report(
        score=result["ats_score"],
        category=result["recommendation"],
        skill_score=result["skill_score"],
        text_similarity=result["text_similarity"],
        experience_score=result["experience_score"],
        matched=matched_skills,
        missing=result["missing_skills"],
        suggestions=result["suggestions"],
        recommended_jobs=recommended_jobs,
    )

    return render_template(
        "index.html",
        score=result["ats_score"],
        category=result["recommendation"],
        matched=matched_skills,
        missing=result["missing_skills"],
        suggestions=result["suggestions"],
        text_similarity=result["text_similarity"],
        skill_score=result["skill_score"],
        experience_score=result["experience_score"],
        recommended_jobs=recommended_jobs,
        pdf_path=pdf_path,
    )


@app.route("/download-report")
def download_report():
    return send_file("reports/ATS_Report.pdf", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
