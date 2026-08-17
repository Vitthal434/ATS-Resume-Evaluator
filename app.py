import os
import threading

from flask import Flask, jsonify, render_template, request, send_file

from resume_parser import read_pdf, read_docx
from matcher import final_match_score, get_semantic_model
from job_recommender import recommend_jobs
from report_generator import generate_report, format_skill
from ai.gemini_provider import is_gemini_available
from ai.resume_improver import improve_resume_bullets
from ai.jd_semantic_parser import parse_job_description
from gap_analyzer import analyze_resume_job_gap, enhance_gap_analysis_with_ai

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "resumeiq-default-dev-key")


def _warmup_model():
    """Pre-warm SentenceTransformer weights in background thread."""
    try:
        get_semantic_model()
    except Exception:
        pass


def start_model_warmup():
    """Start background model pre-warming daemon thread."""
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or os.environ.get("WERKZEUG_RUN_MAIN") is None:
        thread = threading.Thread(target=_warmup_model, daemon=True, name="ModelWarmupThread")
        thread.start()


start_model_warmup()

app.jinja_env.filters["format_skill"] = format_skill


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/analyze")
def analyze():
    return render_template("analyze.html")


@app.route("/match", methods=["POST"])
def match():
    resume = request.files["resume"]
    job_desc = request.form["job_description"]

    # Validate file extension
    ext = os.path.splitext(resume.filename)[1].lower() if resume.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        resume_text = ""
    else:
        # Extract text from the uploaded resume.
        try:
            if ext == ".pdf":
                resume_text = read_pdf(resume)
            else:
                resume_text = read_docx(resume)
        except ValueError:
            resume_text = ""

    # Pass raw text to the matcher.
    # matcher.py performs its own normalization while preserving
    # punctuation and structural keywords such as "or".

    # Generate the ATS result, job recommendations, downloadable report, and gap analysis.
    result = final_match_score(resume_text, job_desc)
    gap_analysis = analyze_resume_job_gap(resume_text, job_desc)

    matched_skills = result["matched_skills"]

    top_recommendation = (
        result["missing_skills"][0] if result["missing_skills"] else None
    )

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
        "dashboard.html",
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
        top_recommendation=top_recommendation,
        gap_analysis=gap_analysis,
    )


@app.route("/download-report")
def download_report():
    return send_file("reports/ATS_Report.pdf", as_attachment=True)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/ai/improve", methods=["POST"])
def ai_improve():
    if not is_gemini_available():
        return jsonify({
            "error": "AI service not configured (GEMINI_API_KEY environment variable is missing).",
            "available": False
        }), 503

    data = request.get_json(silent=True) or request.form
    resume_text = data.get("resume_text", "").strip()
    job_description = data.get("job_description", "").strip()
    missing_skills = data.get("missing_skills", [])

    if not resume_text or not job_description:
        return jsonify({"error": "Missing required fields: resume_text and job_description."}), 400

    result = improve_resume_bullets(resume_text, job_description, missing_skills)

    if result.get("error") and not result.get("improvements"):
        return jsonify({"error": result["error"], "available": True}), 500

    return jsonify(result), 200


@app.route("/api/ai/parse-jd", methods=["POST"])
def ai_parse_jd():
    if not is_gemini_available():
        return jsonify({"error": "Gemini AI is not configured"}), 503

    data = request.get_json(silent=True) or request.form
    job_description = data.get("job_description", "").strip()

    if not job_description:
        return jsonify({"error": "Job description is required"}), 400

    result = parse_job_description(job_description)

    if result.get("error") or not result.get("available"):
        return jsonify({"error": "Unable to semantically parse job description"}), 500

    return jsonify({"success": True, "analysis": result["analysis"]}), 200


@app.route("/api/gap-analysis", methods=["POST"])
def api_gap_analysis():
    data = request.get_json(silent=True) or request.form
    resume_text = data.get("resume_text", "").strip()
    job_description = data.get("job_description", "").strip()
    include_ai = data.get("include_ai", False)

    if not resume_text or not job_description:
        return jsonify({"error": "Missing required fields: resume_text and job_description."}), 400

    gap_res = analyze_resume_job_gap(resume_text, job_description)

    if include_ai:
        gap_res = enhance_gap_analysis_with_ai(gap_res, job_description)

    return jsonify({"success": True, "analysis": gap_res}), 200


@app.route("/api/ai/improvement-roadmap", methods=["POST"])
def ai_improvement_roadmap():
    if not is_gemini_available():
        return jsonify({"error": "Gemini AI is not configured"}), 503

    data = request.get_json(silent=True) or request.form
    resume_text = data.get("resume_text", "").strip()
    job_description = data.get("job_description", "").strip()

    if not resume_text or not job_description:
        return jsonify({"error": "Missing required fields: resume_text and job_description."}), 400

    gap_res = analyze_resume_job_gap(resume_text, job_description)
    gap_res = enhance_gap_analysis_with_ai(gap_res, job_description)

    return jsonify({
        "success": True,
        "roadmap": gap_res.get("roadmap"),
        "ai_roadmap": gap_res.get("ai_roadmap")
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
