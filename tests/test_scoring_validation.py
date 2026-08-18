"""
Stage 1 — Scoring Engine Validation Suite
==========================================
Validates BEHAVIOR of the current ATS scoring pipeline.
This is NOT an accuracy measurement against ground truth.
All observed results are printed verbatim for manual review.

Covers:
  TC-01  Identical resume / JD
  TC-02  Strongly related resume / JD
  TC-03  Completely unrelated resume / JD
  TC-04  Empty resume
  TC-05  Empty JD
  TC-06  Frontend resume vs Frontend JD
  TC-07  Backend resume vs Backend JD
  TC-08  ML/NLP resume vs ML/NLP JD
  TC-09  Frontend resume vs Backend JD (cross-domain mismatch)
  TC-10  Backend resume vs ML JD (cross-domain mismatch)
  TC-11  Skill alias / canonicalization
  TC-12  Missing required skills
  TC-13  Optional / nice-to-have skills
  TC-14  Experience scoring
  TC-15  Final weighted ATS score composition

Run:
    python -m pytest tests/test_scoring_validation.py -v
  or
    python tests/test_scoring_validation.py
"""

import sys
import os
import textwrap
import unittest

# -----------------------------------------------------------------------
# Ensure project root is on the path so imports work whether tests are
# invoked from the project root or from the tests/ sub-directory.
# -----------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from matcher import (
    extract_skills,
    parse_job_description,
    calculate_skill_match,
    experience_score,
    final_match_score,
    extract_alternative_requirements,
    calculate_weighted_skill_score,
    calculate_text_similarity,
)


# =====================================================================
# CANONICAL SAMPLE JOB DESCRIPTIONS
# =====================================================================

JD_FRONTEND = textwrap.dedent("""\
    Frontend Software Engineer

    We are looking for a skilled Frontend Software Engineer to join our team.

    Required Skills:
    - Proficiency in JavaScript and TypeScript
    - Strong knowledge of React.js or Vue.js
    - Experience with HTML and CSS
    - Familiarity with RESTful APIs

    Preferred Skills:
    - Experience with testing frameworks such as Jest
    - Knowledge of webpack or Vite
    - Experience with Git and version control

    The ideal candidate has 3+ years of experience building web applications.
""")

JD_BACKEND = textwrap.dedent("""\
    Senior Backend Software Engineer

    We are seeking an experienced backend engineer for our infrastructure team.

    Required Qualifications:
    - Strong proficiency in Python or Go
    - Experience with Django or FastAPI
    - Solid understanding of PostgreSQL and Redis
    - Knowledge of REST API design
    - Docker and container orchestration

    Nice to Have:
    - AWS or GCP cloud experience
    - Familiarity with Kubernetes
    - Experience with Kafka or RabbitMQ

    Minimum 5 years of professional experience required.
""")

JD_ML_NLP = textwrap.dedent("""\
    Senior Machine Learning Engineer - NLP

    We are looking for an experienced ML engineer specializing in NLP.

    Required Skills:
    - Expert-level Python programming
    - Deep knowledge of NLP and Transformers
    - Hands-on experience with PyTorch or TensorFlow
    - Experience with Hugging Face library
    - Strong understanding of machine learning fundamentals

    Preferred Qualifications:
    - Experience with BERT or RoBERTa models
    - Knowledge of LangChain or LlamaIndex
    - Familiarity with MLflow or DVC
    - Experience with Docker

    At least 4 years of experience in machine learning or NLP.
""")


# =====================================================================
# CANONICAL SAMPLE RESUMES
# =====================================================================

RESUME_FRONTEND = textwrap.dedent("""\
    Jane Doe — Frontend Developer
    5 years of experience building modern web applications.

    Skills:
    JavaScript, TypeScript, React.js, HTML, CSS, Jest, webpack, Git

    Experience:
    - Developed React-based SPAs with TypeScript
    - Integrated RESTful APIs in web applications
    - Wrote unit tests using Jest
    - Used Git for version control and code reviews
""")

RESUME_BACKEND = textwrap.dedent("""\
    John Smith — Senior Backend Engineer
    6 years of professional experience in backend systems.

    Skills:
    Python, Go, Django, FastAPI, PostgreSQL, Redis, Docker, REST API, Git

    Experience:
    - Designed and built REST APIs with Django and FastAPI
    - Managed PostgreSQL and Redis in production
    - Containerized services using Docker
    - Deployed on AWS with EC2 and RDS
""")

RESUME_ML_NLP = textwrap.dedent("""\
    Alice Chen — Machine Learning Engineer
    5 years of experience in ML and NLP research and production.

    Skills:
    Python, PyTorch, NLP, Transformers, Hugging Face, BERT, scikit-learn,
    machine learning, deep learning, LangChain, Docker, Git

    Experience:
    - Built NLP pipelines using BERT and RoBERTa with Hugging Face
    - Trained deep learning models with PyTorch
    - Applied fine-tuning techniques on LLMs
    - Integrated LangChain for RAG applications
""")

RESUME_UNRELATED = textwrap.dedent("""\
    Bob Builder — Construction Site Manager
    10 years managing large-scale construction projects.

    Skills:
    Project management, site safety, concrete, steel, civil engineering,
    AutoCAD, cost estimation, budget management

    Experience:
    - Supervised 50+ construction workers on high-rise projects
    - Managed budgets up to $5 million
    - Ensured regulatory compliance on all builds
""")


# =====================================================================
# HELPERS
# =====================================================================

SEPARATOR = "=" * 70


def _header(tc_id, title):
    print(f"\n{SEPARATOR}")
    print(f"  {tc_id}: {title}")
    print(SEPARATOR)


def _report(label, value):
    print(f"  {label:<30} {value}")


def _flag(condition, message):
    """Print a SUSPICIOUS flag when condition is True."""
    if condition:
        print(f"  [SUSPICIOUS] {message}")


# =====================================================================
# TEST CLASS
# =====================================================================

class TestScoringValidation(unittest.TestCase):

    # -----------------------------------------------------------------
    # TC-01  Identical resume / JD
    # -----------------------------------------------------------------
    def test_01_identical_resume_jd(self):
        """
        EXPECTATION: ATS score should be very high (>= 80).
        Skill score should be >= 80. Text similarity should be >= 80.
        """
        _header("TC-01", "Identical resume / JD text")
        result = final_match_score(JD_FRONTEND, JD_FRONTEND)

        _report("ATS Score",         result["ats_score"])
        _report("Skill Score",       result["skill_score"])
        _report("Text Similarity",   result["text_similarity"])
        _report("Experience Score",  result["experience_score"])
        _report("Matched Skills",    result["matched_skills"])
        _report("Missing Skills",    result["missing_skills"])

        _flag(result["ats_score"] < 80,
              f"Identical text scored only {result['ats_score']}% — expected >= 80%.")
        _flag(result["text_similarity"] < 80,
              f"Identical text similarity {result['text_similarity']}% — expected >= 80%.")

        self.assertGreaterEqual(result["ats_score"], 70,
            "Identical resume/JD produced unexpectedly low ATS score.")
        self.assertGreaterEqual(result["text_similarity"], 70,
            "Identical text should produce high text similarity.")

    # -----------------------------------------------------------------
    # TC-02  Strongly related resume / JD
    # -----------------------------------------------------------------
    def test_02_strongly_related(self):
        """
        EXPECTATION: Frontend resume vs Frontend JD — high score (>= 65).
        """
        _header("TC-02", "Strongly related — Frontend resume vs Frontend JD")
        result = final_match_score(RESUME_FRONTEND, JD_FRONTEND)

        _report("ATS Score",        result["ats_score"])
        _report("Skill Score",      result["skill_score"])
        _report("Text Similarity",  result["text_similarity"])
        _report("Matched Skills",   result["matched_skills"])
        _report("Missing Skills",   result["missing_skills"])

        _flag(result["ats_score"] < 55,
              f"Strongly matched pair scored only {result['ats_score']}% — expected >= 55%.")

        self.assertGreaterEqual(result["ats_score"], 50,
            "Strongly related resume/JD produced unexpectedly low score.")

    # -----------------------------------------------------------------
    # TC-03  Completely unrelated resume / JD
    # -----------------------------------------------------------------
    def test_03_unrelated(self):
        """
        EXPECTATION: Construction resume vs Frontend JD — low score (<= 60).
        Almost no skill matches. Missing skills list should be non-empty.
        """
        _header("TC-03", "Completely unrelated — Construction resume vs Frontend JD")
        result = final_match_score(RESUME_UNRELATED, JD_FRONTEND)

        _report("ATS Score",        result["ats_score"])
        _report("Skill Score",      result["skill_score"])
        _report("Text Similarity",  result["text_similarity"])
        _report("Matched Skills",   result["matched_skills"])
        _report("Missing Skills",   result["missing_skills"])

        _flag(result["skill_score"] > 20,
              f"Unrelated resume has skill score {result['skill_score']}% — expected <= 20%.")
        _flag(result["ats_score"] > 65,
              f"Unrelated pair scored {result['ats_score']}% — seems too high.")

        self.assertEqual(result["matched_skills"], [],
            "Unrelated resume should have no matched skills.")
        self.assertGreater(len(result["missing_skills"]), 0,
            "Missing skills list should be non-empty for unrelated resume.")

    # -----------------------------------------------------------------
    # TC-04  Empty resume
    # -----------------------------------------------------------------
    def test_04_empty_resume(self):
        """
        EXPECTATION: ATS score should be very low. No matched skills.
        Should NOT raise an exception.
        """
        _header("TC-04", "Empty resume")
        result = final_match_score("", JD_FRONTEND)

        _report("ATS Score",       result["ats_score"])
        _report("Skill Score",     result["skill_score"])
        _report("Text Similarity", result["text_similarity"])
        _report("Matched Skills",  result["matched_skills"])

        _flag(result["ats_score"] > 30,
              f"Empty resume scored {result['ats_score']}% — expected a very low score.")

        self.assertEqual(result["matched_skills"], [],
            "Empty resume should have zero matched skills.")
        self.assertEqual(result["skill_score"], 0,
            "Empty resume should have 0 skill score.")
        self.assertEqual(result["text_similarity"], 0.0,
            "Empty resume should have 0 text similarity.")
        self.assertEqual(result["experience_score"], 0,
            "Empty resume should have 0 experience score.")
        self.assertEqual(result["ats_score"], 0.0,
            "Empty resume should have 0 ATS score.")

    # -----------------------------------------------------------------
    # TC-05  Empty JD
    # -----------------------------------------------------------------
    def test_05_empty_jd(self):
        """
        EXPECTATION: Should NOT raise. Skill score = 0 (no JD skills to match).
        Behavior: calculate_skill_match returns 0 when all_job_skills is empty.
        """
        _header("TC-05", "Empty JD")
        result = final_match_score(RESUME_FRONTEND, "")

        _report("ATS Score",       result["ats_score"])
        _report("Skill Score",     result["skill_score"])
        _report("Text Similarity", result["text_similarity"])
        _report("Matched Skills",  result["matched_skills"])

        _flag(result["skill_score"] != 0,
              f"Empty JD yielded non-zero skill score: {result['skill_score']}.")

        self.assertEqual(result["skill_score"], 0,
            "Empty JD should produce zero skill score.")

    # -----------------------------------------------------------------
    # TC-06  Frontend resume vs Frontend JD
    # -----------------------------------------------------------------
    def test_06_frontend_vs_frontend(self):
        """
        EXPECTATION: Good match. Skill score >= 60. Matched skills include
        javascript, typescript, react, html, css, git.
        """
        _header("TC-06", "Frontend resume vs Frontend JD")
        skill_score, matched, missing = calculate_skill_match(RESUME_FRONTEND, JD_FRONTEND)

        _report("Skill Score",    skill_score)
        _report("Matched Skills", matched)
        _report("Missing Skills", missing)

        expected = {"javascript", "typescript", "react.js", "html", "css", "git", "jest"}
        for skill in ["javascript", "typescript", "html", "css"]:
            _flag(skill not in matched,
                  f"'{skill}' not matched for Frontend resume vs Frontend JD.")

        _flag(skill_score < 50,
              f"Frontend-to-Frontend skill score {skill_score}% — expected >= 50%.")

        self.assertGreaterEqual(skill_score, 40,
            "Frontend resume vs Frontend JD should have decent skill score.")

    # -----------------------------------------------------------------
    # TC-07  Backend resume vs Backend JD
    # -----------------------------------------------------------------
    def test_07_backend_vs_backend(self):
        """
        EXPECTATION: Good match. Matched skills include python/go, django/fastapi,
        postgresql, docker, redis.
        """
        _header("TC-07", "Backend resume vs Backend JD")
        skill_score, matched, missing = calculate_skill_match(RESUME_BACKEND, JD_BACKEND)

        _report("Skill Score",    skill_score)
        _report("Matched Skills", matched)
        _report("Missing Skills", missing)

        for skill in ["python", "django", "postgresql", "docker"]:
            _flag(skill not in matched,
                  f"'{skill}' not matched in Backend resume vs Backend JD.")

        _flag(skill_score < 50,
              f"Backend-to-Backend skill score {skill_score}% — expected >= 50%.")

        self.assertGreaterEqual(skill_score, 40,
            "Backend resume vs Backend JD should have a reasonable skill score.")

    # -----------------------------------------------------------------
    # TC-08  ML/NLP resume vs ML/NLP JD
    # -----------------------------------------------------------------
    def test_08_ml_vs_ml(self):
        """
        EXPECTATION: High skill match. Skills like python, pytorch, nlp,
        transformers, hugging face, bert should all be matched.
        """
        _header("TC-08", "ML/NLP resume vs ML/NLP JD")
        skill_score, matched, missing = calculate_skill_match(RESUME_ML_NLP, JD_ML_NLP)

        _report("Skill Score",    skill_score)
        _report("Matched Skills", matched)
        _report("Missing Skills", missing)

        for skill in ["python", "natural language processing", "pytorch", "transformers",
                      "hugging face", "machine learning"]:
            _flag(skill not in matched,
                  f"'{skill}' not matched in ML/NLP resume vs ML/NLP JD.")

        _flag(skill_score < 55,
              f"ML/NLP-to-ML/NLP skill score {skill_score}% — expected >= 55%.")

        self.assertGreaterEqual(skill_score, 45,
            "ML resume vs ML JD should have a high skill score.")

    # -----------------------------------------------------------------
    # TC-09  Frontend resume vs Backend JD (cross-domain mismatch)
    # -----------------------------------------------------------------
    def test_09_frontend_vs_backend(self):
        """
        EXPECTATION: Low skill match. Frontend skills (React, HTML, CSS)
        are irrelevant to Backend JD.
        """
        _header("TC-09", "Frontend resume vs Backend JD (cross-domain)")
        skill_score, matched, missing = calculate_skill_match(RESUME_FRONTEND, JD_BACKEND)

        _report("Skill Score",    skill_score)
        _report("Matched Skills", matched)
        _report("Missing Skills", missing)

        _flag(skill_score > 50,
              f"Frontend vs Backend skill score {skill_score}% — expected a lower mismatch score.")

        # Git might match — that's valid. But core backend skills should be missing.
        for skill in ["python", "go", "postgresql", "redis", "docker"]:
            _flag(skill in matched,
                  f"'{skill}' unexpectedly matched — Frontend resume should not have it.")

    # -----------------------------------------------------------------
    # TC-10  Backend resume vs ML JD (cross-domain mismatch)
    # -----------------------------------------------------------------
    def test_10_backend_vs_ml(self):
        """
        EXPECTATION: Low-medium skill match. Python may appear in both.
        NLP/ML-specific skills should largely be missing.
        """
        _header("TC-10", "Backend resume vs ML JD (cross-domain)")
        skill_score, matched, missing = calculate_skill_match(RESUME_BACKEND, JD_ML_NLP)

        _report("Skill Score",    skill_score)
        _report("Matched Skills", matched)
        _report("Missing Skills", missing)

        for skill in ["natural language processing", "pytorch", "transformers", "hugging face"]:
            _flag(skill in matched,
                  f"'{skill}' unexpectedly matched — Backend resume should not have it.")

        _flag(skill_score > 45,
              f"Backend vs ML skill score {skill_score}% — expected a lower cross-domain score.")

    # -----------------------------------------------------------------
    # TC-11  Skill alias / canonicalization
    # -----------------------------------------------------------------
    def test_11_alias_canonicalization(self):
        """
        EXPECTATION: Aliases resolve to canonical names.
        - 'py' → 'python'
        - 'js' → 'javascript'
        - 'ts' → 'typescript'
        - 'sklearn' → 'scikit-learn'
        - 'nlp' → 'natural language processing'
        - 'ml' → 'machine learning'
        - 'tf' → 'tensorflow'
        - 'golang' → 'go'
        """
        _header("TC-11", "Skill alias / canonicalization")
        test_cases = [
            ("py",      "python"),
            ("js",      "javascript"),
            ("ts",      "typescript"),
            ("sklearn", "scikit-learn"),
            ("nlp",     "natural language processing"),
            ("ml",      "machine learning"),
            ("tf",      "tensorflow"),
            ("golang",  "go"),
        ]

        all_passed = True
        for alias, canonical in test_cases:
            found = extract_skills(alias)
            resolved = canonical in found
            status = "OK" if resolved else "FAIL"
            _report(f"'{alias}' -> '{canonical}'", status)
            if not resolved:
                all_passed = False
                print(f"  [SUSPICIOUS] alias '{alias}' did NOT resolve to '{canonical}'."
                      f"  Got: {found}")

        self.assertTrue(all_passed,
            "One or more aliases did not resolve to their canonical skill.")

    # -----------------------------------------------------------------
    # TC-12  Missing required skills
    # -----------------------------------------------------------------
    def test_12_missing_required_skills(self):
        """
        EXPECTATION: When resume has no relevant skills for the JD,
        missing_skills should contain the required JD skills.
        """
        _header("TC-12", "Missing required skills")
        skill_score, matched, missing = calculate_skill_match(RESUME_UNRELATED, JD_BACKEND)

        _report("Skill Score",    skill_score)
        _report("Matched Skills", matched)
        _report("Missing Skills", missing)

        _flag(len(missing) == 0,
              "Missing skills list is empty for an unrelated resume — expected required skills to be listed.")

        self.assertGreater(len(missing), 0,
            "Missing skills list should contain JD required skills for an unrelated resume.")
        self.assertEqual(matched, [],
            "Matched skills should be empty for a completely unrelated resume.")

    # -----------------------------------------------------------------
    # TC-13  Optional / nice-to-have skills
    # -----------------------------------------------------------------
    def test_13_optional_skills(self):
        """
        EXPECTATION: Optional skills are parsed correctly.
        Backend JD has 'Nice to Have' section with aws/gcp, kubernetes, kafka/rabbitmq.
        These should appear in optional_skills (not required).
        """
        _header("TC-13", "Optional / nice-to-have skills")
        job_data = parse_job_description(JD_BACKEND)

        _report("Required Skills",  sorted(job_data["required"]))
        _report("Optional Skills",  sorted(job_data["optional"]))
        _report("Required OR-Alts", job_data["required_alternatives"])
        _report("Optional OR-Alts", job_data["optional_alternatives"])

        # Verify the optional section was actually parsed
        _flag(len(job_data["optional"]) == 0,
              "Optional skills list is empty — 'Nice to Have' section may not be parsed.")

        # AWS/GCP should appear as an OR alternative in optional
        optional_or_alts = job_data["optional_alternatives"]
        aws_gcp_group_found = any(
            {"aws", "gcp"}.issubset(set(group)) for group in optional_or_alts
        )
        _flag(not aws_gcp_group_found,
              "AWS/GCP OR-alternative not found in optional_alternatives — may indicate OR parsing issue.")

        self.assertGreater(len(job_data["optional"]), 0,
            "Optional skills should be parsed from 'Nice to Have' section.")

    # -----------------------------------------------------------------
    # TC-14  Experience scoring
    # -----------------------------------------------------------------
    def test_14_experience_scoring(self):
        """
        EXPECTATION:
        - '5 years' → score between 70 and 100
        - '6 months' → score between 60 and 80
        - Student keywords (intern, project) → score around 65
        - No experience → score around 50
        """
        _header("TC-14", "Experience scoring")

        cases = [
            ("5 years of professional software engineering experience", 70, 100, "5 years"),
            ("worked for 18 months as a developer", 60, 85, "18 months"),
            ("completed internship and several projects", 60, 80, "internship/project"),
            ("I am a fresh graduate with no experience", 45, 60, "no experience"),
        ]

        all_passed = True
        for text, lo, hi, label in cases:
            score = experience_score(text)
            ok = lo <= score <= hi
            status = "OK" if ok else f"FAIL (got {score}, expected {lo}-{hi})"
            _report(f"[{label}]", f"{score}% -> {status}")
            if not ok:
                all_passed = False
                _flag(True, f"Experience score {score}% for '{label}' is outside expected range [{lo}-{hi}].")

        self.assertTrue(all_passed,
            "One or more experience score cases returned an unexpected value.")

    # -----------------------------------------------------------------
    # TC-15  Final weighted ATS score composition
    # -----------------------------------------------------------------
    def test_15_weighted_ats_score(self):
        """
        EXPECTATION:
        - Weights: Skill 50%, Text 30%, Experience 20%
        - final_score = round(0.50 * skill + 0.30 * text + 0.20 * exp, 2)
        - Verify the arithmetic is correct by recomputing manually.
        """
        _header("TC-15", "Final weighted ATS score composition")

        SKILL_WEIGHT = 0.50
        TEXT_WEIGHT = 0.30
        EXPERIENCE_WEIGHT = 0.20

        result = final_match_score(RESUME_BACKEND, JD_BACKEND)

        s = result["skill_score"]
        t = result["text_similarity"]
        e = result["experience_score"]
        reported = result["ats_score"]

        expected = round(SKILL_WEIGHT * s + TEXT_WEIGHT * t + EXPERIENCE_WEIGHT * e, 2)

        _report("Skill Score",        s)
        _report("Text Similarity",    t)
        _report("Experience Score",   e)
        _report("Reported ATS Score", reported)
        _report("Recomputed Score",   expected)
        _report("Recommendation",     result["recommendation"])

        match_ok = abs(reported - expected) < 0.1
        _flag(not match_ok,
              f"ATS score arithmetic mismatch: reported={reported}, recomputed={expected}.")

        self.assertAlmostEqual(reported, expected, places=1,
            msg=f"ATS score arithmetic mismatch: reported={reported}, expected={expected}.")

    # -----------------------------------------------------------------
    # TC-16  Job recommender canonical matching
    # -----------------------------------------------------------------
    def test_16_job_recommender(self):
        """
        EXPECTATION: Frontend resume skills (including canonical react.js and rest api)
        should recommend Frontend/React Developer with high match score.
        """
        _header("TC-16", "Job recommender canonical skill matching")

        from job_recommender import recommend_jobs
        frontend_skills = ["javascript", "typescript", "react.js", "html", "css", "git", "rest api"]

        recs = recommend_jobs(frontend_skills)
        _report("Top recommendation", recs[0]["job"] if recs else "None")
        _report("Top score", f"{recs[0]['score']}%" if recs else "0%")

        rec_jobs = [r["job"] for r in recs]
        self.assertIn("React Developer", rec_jobs)
        self.assertIn("Frontend Developer", rec_jobs)
        self.assertGreaterEqual(recs[0]["score"], 80)



# =====================================================================
# MAIN — can also be run directly as a script
# =====================================================================

if __name__ == "__main__":
    print("\nResumeIQ — Stage 1 Scoring Engine Validation")
    print("=" * 70)
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = None  # Preserve declaration order
    suite = loader.loadTestsFromTestCase(TestScoringValidation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
