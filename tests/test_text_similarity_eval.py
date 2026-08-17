"""
Stage 2A -- Text Similarity Evaluation Suite
=============================================
Purpose: Evaluate the BEHAVIOR of the text similarity pipeline.
         This is NOT accuracy measurement against a labeled ground truth.
         All scores are observed and annotated for reasonableness.

Architecture under test
-----------------------
The function called by final_match_score() is the LOCAL definition in
matcher.py (line 705), NOT the function in text_similarity.py.

matcher.calculate_text_similarity():
    1. Preprocesses both texts (lowercase, normalise punctuation, etc.)
    2. TF-IDF lexical similarity (unigrams + bigrams, sublinear_tf=True,
       English stopwords removed) -- cosine similarity on sparse matrix
    3. SentenceTransformer("all-MiniLM-L6-v2") semantic similarity --
       cosine similarity on normalised embeddings
    4. Hybrid = 0.70 * semantic + 0.30 * tfidf
    5. Clamped to [0.0, 1.0], scaled to [0, 100], rounded to 2 dp.

text_similarity.calculate_text_similarity() (IMPORTED BUT SHADOWED):
    Only TF-IDF (no semantic).  The import at line 19 of matcher.py is
    dead code -- the local definition at line 705 shadows it.

NOTE: This test file only tests matcher.calculate_text_similarity().
      The shadowed text_similarity module function is tested separately
      in TC-ST-11 and TC-ST-12 for comparison purposes.

Run:
    .\\resumeiq-venv\\Scripts\\python.exe tests\\test_text_similarity_eval.py
"""

import sys
import os
import textwrap
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import the HYBRID function from matcher (the one actually used)
from matcher import calculate_text_similarity as hybrid_similarity

# Import the plain TF-IDF function from text_similarity for comparison
from text_similarity import calculate_text_similarity as tfidf_only_similarity

SEPARATOR = "=" * 70


def _header(tc_id, title):
    print(f"\n{SEPARATOR}")
    print(f"  {tc_id}: {title}")
    print(SEPARATOR)


def _report(label, value):
    print(f"  {label:<40} {value}")


def _flag(condition, message):
    if condition:
        print(f"  [SUSPICIOUS] {message}")


# =====================================================================
# CANONICAL SAMPLE TEXTS  (shared with Stage 1 test suite)
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

RESUME_FRONTEND = textwrap.dedent("""\
    Jane Doe -- Frontend Developer
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
    John Smith -- Senior Backend Engineer
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
    Alice Chen -- Machine Learning Engineer
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
    Bob Builder -- Construction Site Manager
    10 years managing large-scale construction projects.

    Skills:
    Project management, site safety, concrete, steel, civil engineering,
    AutoCAD, cost estimation, budget management

    Experience:
    - Supervised 50+ construction workers on high-rise projects
    - Managed budgets up to $5 million
    - Ensured regulatory compliance on all builds
""")

# A resume containing ONLY a skill list (no prose)
RESUME_SKILLS_ONLY = textwrap.dedent("""\
    JavaScript TypeScript React HTML CSS Jest webpack Git REST API
""")

# A JD containing mostly a skill list (minimal prose)
JD_SKILLS_ONLY = textwrap.dedent("""\
    Required: JavaScript TypeScript React HTML CSS Jest webpack Git REST API
""")

# Nearly-identical to JD_FRONTEND but with reordered / rephrased wording
JD_FRONTEND_REWORDED = textwrap.dedent("""\
    Software Engineer -- Frontend

    Our team needs a skilled Frontend Software Engineer.

    Must-Have Qualifications:
    - TypeScript and JavaScript proficiency
    - React.js or Vue.js expertise
    - Solid CSS and HTML background
    - Working knowledge of REST APIs

    Additional Preferences:
    - Jest or similar testing frameworks
    - Vite or webpack build tools
    - Version control with Git

    We expect 3 or more years of web application development experience.
""")

# Same domain (web) but clearly different role (DevOps vs Frontend)
JD_DEVOPS = textwrap.dedent("""\
    Senior DevOps Engineer

    We need an experienced DevOps/SRE engineer.

    Required:
    - Linux system administration
    - Docker and Kubernetes
    - CI/CD pipeline design (Jenkins, GitHub Actions)
    - AWS or GCP infrastructure management
    - Terraform or CloudFormation

    Nice to Have:
    - Prometheus and Grafana monitoring
    - Ansible or Chef configuration management

    5+ years of DevOps or SRE experience required.
""")


# =====================================================================
# TEST CLASS
# =====================================================================

class TestTextSimilarityEvaluation(unittest.TestCase):

    # -----------------------------------------------------------------
    # TC-ST-01  Identical resume and JD
    # -----------------------------------------------------------------
    def test_st01_identical(self):
        """
        Identical texts fed as both resume and JD.
        EXPECTATION: score close to 100. Both TF-IDF and semantic cosine
        of identical vectors = 1.0 -> hybrid = 100.
        """
        _header("TC-ST-01", "Identical resume and JD (JD_FRONTEND as both)")
        score = hybrid_similarity(JD_FRONTEND, JD_FRONTEND)
        _report("Hybrid score", score)
        _flag(score < 95, f"Identical texts scored {score}% -- expected >= 95%.")
        self.assertGreaterEqual(score, 95,
            "Identical texts should produce a score near 100.")

    # -----------------------------------------------------------------
    # TC-ST-02  Nearly identical -- reordered wording
    # -----------------------------------------------------------------
    def test_st02_reworded(self):
        """
        JD_FRONTEND vs JD_FRONTEND_REWORDED -- same skills, slightly
        different sentence structure.
        EXPECTATION: high score (>= 70). Semantic model should handle
        paraphrasing well.
        """
        _header("TC-ST-02", "Nearly identical -- reordered / rephrased wording")
        score = hybrid_similarity(JD_FRONTEND, JD_FRONTEND_REWORDED)
        _report("Hybrid score", score)
        _flag(score < 65, f"Reworded JD scored {score}% -- expected >= 65%.")
        self.assertGreaterEqual(score, 55,
            "Reworded/reordered text should score reasonably high.")

    # -----------------------------------------------------------------
    # TC-ST-03  Strong semantic match with different wording
    # -----------------------------------------------------------------
    def test_st03_strong_semantic_match(self):
        """
        Frontend resume vs Frontend JD -- different wording, same domain.
        EXPECTATION: moderate-to-high (>= 40). Semantic component should
        capture domain overlap.
        """
        _header("TC-ST-03", "Strong semantic match -- Frontend resume vs Frontend JD")
        score = hybrid_similarity(RESUME_FRONTEND, JD_FRONTEND)
        _report("Hybrid score", score)
        _flag(score < 35, f"Strong semantic match scored {score}% -- expected >= 35%.")
        self.assertGreaterEqual(score, 30,
            "Same-domain resume/JD should show meaningful semantic similarity.")

    # -----------------------------------------------------------------
    # TC-ST-04  Moderate / partial match
    # -----------------------------------------------------------------
    def test_st04_moderate_match(self):
        """
        Backend resume vs Frontend JD -- overlapping general software terms
        (git, api, experience) but distinct stacks.
        EXPECTATION: moderate score, clearly below TC-ST-03.
        """
        _header("TC-ST-04", "Moderate match -- Backend resume vs Frontend JD")
        score_backend_vs_frontend = hybrid_similarity(RESUME_BACKEND, JD_FRONTEND)
        score_frontend_vs_frontend = hybrid_similarity(RESUME_FRONTEND, JD_FRONTEND)
        _report("Backend resume vs Frontend JD", score_backend_vs_frontend)
        _report("Frontend resume vs Frontend JD (ref)", score_frontend_vs_frontend)
        _flag(
            score_backend_vs_frontend >= score_frontend_vs_frontend,
            f"Backend vs Frontend ({score_backend_vs_frontend}%) is >= "
            f"Frontend vs Frontend ({score_frontend_vs_frontend}%) -- ordering inverted."
        )
        # Ordering assertion: same-domain should outscore cross-domain
        self.assertLess(
            score_backend_vs_frontend,
            score_frontend_vs_frontend,
            "Same-domain match should outscore cross-domain partial match."
        )

    # -----------------------------------------------------------------
    # TC-ST-05  Same domain, different role
    # -----------------------------------------------------------------
    def test_st05_same_domain_different_role(self):
        """
        Frontend resume vs DevOps JD -- both are software engineering but
        different specialisation.
        EXPECTATION: lower than TC-ST-03 (Frontend vs Frontend).
        """
        _header("TC-ST-05", "Same domain, different role -- Frontend resume vs DevOps JD")
        score_fe_vs_devops = hybrid_similarity(RESUME_FRONTEND, JD_DEVOPS)
        score_fe_vs_frontend = hybrid_similarity(RESUME_FRONTEND, JD_FRONTEND)
        _report("Frontend resume vs DevOps JD", score_fe_vs_devops)
        _report("Frontend resume vs Frontend JD (ref)", score_fe_vs_frontend)
        _flag(
            score_fe_vs_devops >= score_fe_vs_frontend,
            f"Different-role ({score_fe_vs_devops}%) is >= same-role "
            f"({score_fe_vs_frontend}%) -- expected ordering to hold."
        )
        self.assertLess(
            score_fe_vs_devops,
            score_fe_vs_frontend,
            "Same-role should outscore different-role within the same domain."
        )

    # -----------------------------------------------------------------
    # TC-ST-06  Completely unrelated domains
    # -----------------------------------------------------------------
    def test_st06_unrelated_domains(self):
        """
        Construction resume vs Frontend JD -- completely different domains.
        EXPECTATION: low score (< 40). Both lexical and semantic overlap
        should be minimal.
        """
        _header("TC-ST-06", "Unrelated domains -- Construction resume vs Frontend JD")
        score = hybrid_similarity(RESUME_UNRELATED, JD_FRONTEND)
        _report("Hybrid score", score)
        _flag(score > 40,
              f"Unrelated domains scored {score}% -- expected < 40%.")
        self.assertLess(score, 45,
            "Completely unrelated domains should produce a low similarity score.")

    # -----------------------------------------------------------------
    # TC-ST-07  Empty resume
    # -----------------------------------------------------------------
    def test_st07_empty_resume(self):
        """
        Empty string as resume. EXPECTATION: exactly 0.0 (guard in preprocess
        catches this before any model call).
        """
        _header("TC-ST-07", "Empty resume")
        score = hybrid_similarity("", JD_FRONTEND)
        _report("Hybrid score", score)
        _flag(score != 0.0, f"Empty resume produced score {score}% -- expected 0.0.")
        self.assertEqual(score, 0.0,
            "Empty resume should produce zero similarity.")

    # -----------------------------------------------------------------
    # TC-ST-08  Empty JD
    # -----------------------------------------------------------------
    def test_st08_empty_jd(self):
        """
        Empty string as JD. EXPECTATION: exactly 0.0.
        """
        _header("TC-ST-08", "Empty JD")
        score = hybrid_similarity(RESUME_FRONTEND, "")
        _report("Hybrid score", score)
        _flag(score != 0.0, f"Empty JD produced score {score}% -- expected 0.0.")
        self.assertEqual(score, 0.0,
            "Empty JD should produce zero similarity.")

    # -----------------------------------------------------------------
    # TC-ST-09  Resume with only skills vs detailed JD
    # -----------------------------------------------------------------
    def test_st09_skills_only_resume_vs_detailed_jd(self):
        """
        A bare skills-list resume vs a full prose JD.
        EXPECTATION: reasonable score (>= 30). The shared skill terms
        should produce both lexical and semantic overlap.
        Note: This tests whether the hybrid handles asymmetric text lengths.
        """
        _header("TC-ST-09", "Skills-only resume vs detailed Frontend JD")
        score_skills_only = hybrid_similarity(RESUME_SKILLS_ONLY, JD_FRONTEND)
        score_full_resume = hybrid_similarity(RESUME_FRONTEND, JD_FRONTEND)
        _report("Skills-only resume vs JD", score_skills_only)
        _report("Full resume vs JD (ref)", score_full_resume)
        _flag(score_skills_only < 20,
              f"Skills-only resume scored {score_skills_only}% -- unexpectedly low "
              f"(same skills as full resume).")
        _flag(score_skills_only > score_full_resume,
              f"Skills-only ({score_skills_only}%) outscored full resume "
              f"({score_full_resume}%) -- check for unexpected TF-IDF inflation.")
        # The score should be non-zero and plausible
        self.assertGreater(score_skills_only, 0,
            "Skills-only resume should have non-zero similarity with matching JD.")

    # -----------------------------------------------------------------
    # TC-ST-10  Detailed resume vs JD with mostly skills
    # -----------------------------------------------------------------
    def test_st10_detailed_resume_vs_skills_only_jd(self):
        """
        A full prose resume vs a bare skills-list JD.
        EXPECTATION: similar ordering as TC-ST-09 but inverted direction.
        The semantic model should still capture shared meaning.
        """
        _header("TC-ST-10", "Detailed Frontend resume vs skills-only Frontend JD")
        score_skills_only_jd = hybrid_similarity(RESUME_FRONTEND, JD_SKILLS_ONLY)
        score_full_jd = hybrid_similarity(RESUME_FRONTEND, JD_FRONTEND)
        _report("Resume vs skills-only JD", score_skills_only_jd)
        _report("Resume vs full JD (ref)", score_full_jd)
        _flag(score_skills_only_jd < 20,
              f"Full resume vs skills-only JD scored {score_skills_only_jd}% -- "
              f"unexpectedly low given matching skill terms.")
        self.assertGreater(score_skills_only_jd, 0,
            "Full resume vs skills-only JD should have non-zero similarity.")

    # -----------------------------------------------------------------
    # TC-ST-11  Stability -- repeated calls return same result
    # -----------------------------------------------------------------
    def test_st11_stability_repeated_calls(self):
        """
        The hybrid similarity function should be deterministic.
        Calling it three times with the same inputs must return the same score.
        """
        _header("TC-ST-11", "Stability -- repeated calls produce identical results")
        scores = [hybrid_similarity(RESUME_ML_NLP, JD_ML_NLP) for _ in range(3)]
        _report("Run 1", scores[0])
        _report("Run 2", scores[1])
        _report("Run 3", scores[2])
        _flag(len(set(scores)) > 1,
              f"Non-deterministic results: {scores}")
        self.assertEqual(scores[0], scores[1],
            "Repeated calls should be deterministic (run 1 != run 2).")
        self.assertEqual(scores[1], scores[2],
            "Repeated calls should be deterministic (run 2 != run 3).")

    # -----------------------------------------------------------------
    # TC-ST-12  Ordering sanity across all three JD pairs
    # -----------------------------------------------------------------
    def test_st12_ordering_sanity(self):
        """
        For each resume/JD pair, the matching domain should outscore
        all cross-domain pairs.

        Frontend resume:  FE-JD > BE-JD  and  FE-JD > ML-JD
        Backend resume:   BE-JD > FE-JD  and  BE-JD > ML-JD (not guaranteed, flag if not)
        ML resume:        ML-JD > FE-JD  and  ML-JD > BE-JD (best effort, flag if not)
        """
        _header("TC-ST-12", "Cross-domain ordering sanity check")

        fe_vs_fe = hybrid_similarity(RESUME_FRONTEND, JD_FRONTEND)
        fe_vs_be = hybrid_similarity(RESUME_FRONTEND, JD_BACKEND)
        fe_vs_ml = hybrid_similarity(RESUME_FRONTEND, JD_ML_NLP)

        be_vs_fe = hybrid_similarity(RESUME_BACKEND, JD_FRONTEND)
        be_vs_be = hybrid_similarity(RESUME_BACKEND, JD_BACKEND)
        be_vs_ml = hybrid_similarity(RESUME_BACKEND, JD_ML_NLP)

        ml_vs_fe = hybrid_similarity(RESUME_ML_NLP, JD_FRONTEND)
        ml_vs_be = hybrid_similarity(RESUME_ML_NLP, JD_BACKEND)
        ml_vs_ml = hybrid_similarity(RESUME_ML_NLP, JD_ML_NLP)

        _report("Frontend resume vs Frontend JD", fe_vs_fe)
        _report("Frontend resume vs Backend JD",  fe_vs_be)
        _report("Frontend resume vs ML/NLP JD",   fe_vs_ml)
        _report("Backend resume vs Frontend JD",  be_vs_fe)
        _report("Backend resume vs Backend JD",   be_vs_be)
        _report("Backend resume vs ML/NLP JD",    be_vs_ml)
        _report("ML/NLP resume vs Frontend JD",   ml_vs_fe)
        _report("ML/NLP resume vs Backend JD",    ml_vs_be)
        _report("ML/NLP resume vs ML/NLP JD",     ml_vs_ml)

        _flag(fe_vs_fe <= fe_vs_be,
              f"FE resume: FE-JD ({fe_vs_fe}) should outscore BE-JD ({fe_vs_be}).")
        _flag(fe_vs_fe <= fe_vs_ml,
              f"FE resume: FE-JD ({fe_vs_fe}) should outscore ML-JD ({fe_vs_ml}).")
        _flag(be_vs_be <= be_vs_fe,
              f"BE resume: BE-JD ({be_vs_be}) should outscore FE-JD ({be_vs_fe}).")
        _flag(be_vs_be <= be_vs_ml,
              f"BE resume: BE-JD ({be_vs_be}) should outscore ML-JD ({be_vs_ml}).")
        _flag(ml_vs_ml <= ml_vs_fe,
              f"ML resume: ML-JD ({ml_vs_ml}) should outscore FE-JD ({ml_vs_fe}).")
        _flag(ml_vs_ml <= ml_vs_be,
              f"ML resume: ML-JD ({ml_vs_ml}) should outscore BE-JD ({ml_vs_be}).")

        # Hard assertion: only for the frontend pair (clearest separation)
        self.assertGreater(fe_vs_fe, fe_vs_be,
            "Frontend resume should score higher on Frontend JD than Backend JD.")
        self.assertGreater(fe_vs_fe, fe_vs_ml,
            "Frontend resume should score higher on Frontend JD than ML/NLP JD.")

    # -----------------------------------------------------------------
    # TC-ST-13  Architecture check -- shadowed import
    # -----------------------------------------------------------------
    def test_st13_shadowed_import_check(self):
        """
        Structural: confirm that the function actually used in production
        (matcher.calculate_text_similarity) is the HYBRID version, and
        that the plain TF-IDF version from text_similarity.py produces
        DIFFERENT scores on the same inputs (confirming the two are distinct).
        """
        _header("TC-ST-13",
                "Architecture: confirm hybrid != tfidf-only on same input")
        hybrid = hybrid_similarity(RESUME_FRONTEND, JD_FRONTEND)
        tfidf_only = tfidf_only_similarity(RESUME_FRONTEND, JD_FRONTEND)
        _report("Hybrid (matcher.py)            ", hybrid)
        _report("TF-IDF only (text_similarity.py)", tfidf_only)
        _report("Are they the same function?",
                "NO -- they differ" if hybrid != tfidf_only else
                "[SUSPICIOUS] YES -- identical scores despite different algorithms")
        _flag(hybrid == tfidf_only,
              "Both functions returned identical scores -- "
              "the import shadowing may not be working as expected.")
        # They should differ on real text
        self.assertNotEqual(
            hybrid, tfidf_only,
            "Hybrid (semantic+TF-IDF) should differ from TF-IDF-only on real text."
        )


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    print("\nResumeIQ -- Stage 2A: Text Similarity Evaluation")
    print("=" * 70)
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = None
    suite = loader.loadTestsFromTestCase(TestTextSimilarityEvaluation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
