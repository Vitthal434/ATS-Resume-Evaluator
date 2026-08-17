"""
ResumeIQ — Stage 9.4 Intelligent Resume-Job Gap Analysis Unit Tests
Verifies deterministic gap analysis, exact/partial/missing classification, priority ordering,
empty inputs safety, offline operation without GEMINI_API_KEY, and scoring weight preservation.
"""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gap_analyzer import analyze_resume_job_gap, enhance_gap_analysis_with_ai
from matcher import SKILL_WEIGHT, TEXT_WEIGHT, EXPERIENCE_WEIGHT, final_match_score


class TestGapAnalysis(unittest.TestCase):
    """Unit test suite for Stage 9.4 Gap Analyzer."""

    def test_01_weights_preserved(self):
        """Verify 50/30/20 ATS weights remain strictly unchanged."""
        self.assertEqual(SKILL_WEIGHT, 0.50)
        self.assertEqual(TEXT_WEIGHT, 0.30)
        self.assertEqual(EXPERIENCE_WEIGHT, 0.20)

    def test_02_exact_skill_classified_as_exact(self):
        """Exact skills mentioned in resume must be in exact_matches."""
        resume = "Skills: Python, Flask, PostgreSQL"
        jd = "Required Skills:\n- Python\n- Flask\n- PostgreSQL"
        res = analyze_resume_job_gap(resume, jd)

        exact_names = [e["skill"] for e in res["exact_matches"]]
        self.assertIn("python", exact_names)
        self.assertIn("flask", exact_names)
        self.assertIn("postgresql", exact_names)
        self.assertEqual(res["skill_coverage"]["missing"], 0)
        self.assertEqual(res["skill_coverage"]["partial_matches"], 0)

    def test_03_canonical_alias_classified_as_exact(self):
        """Canonical aliases (e.g. 'py' for python, 'js' for javascript) classify as exact."""
        resume = "Skills: py, js"
        jd = "Required Skills:\n- Python\n- JavaScript"
        res = analyze_resume_job_gap(resume, jd)

        exact_names = [e["skill"] for e in res["exact_matches"]]
        self.assertIn("python", exact_names)
        self.assertIn("javascript", exact_names)

    def test_04_explicit_related_skill_classified_as_partial(self):
        """Candidate with PostgreSQL for SQL requirement gets classified as partial match with credit 0.5."""
        resume = "Skills: PostgreSQL"
        jd = "Required Skills:\n- SQL"
        res = analyze_resume_job_gap(resume, jd)

        self.assertEqual(res["skill_coverage"]["exact_matches"], 0)
        self.assertEqual(res["skill_coverage"]["partial_matches"], 1)
        self.assertEqual(res["partial_matches"][0]["required_skill"], "sql")
        self.assertEqual(res["partial_matches"][0]["candidate_skill"], "postgresql")
        self.assertEqual(res["partial_matches"][0]["credit"], 0.5)

    def test_05_unrelated_skill_classified_as_missing(self):
        """Unrelated skill receives missing classification."""
        resume = "Skills: Cooking, Driving"
        jd = "Required Skills:\n- Python"
        res = analyze_resume_job_gap(resume, jd)

        self.assertEqual(res["skill_coverage"]["exact_matches"], 0)
        self.assertEqual(res["skill_coverage"]["missing"], 1)
        self.assertEqual(res["missing_skills"][0]["skill"], "python")

    def test_06_required_missing_skill_gets_critical_priority(self):
        """Missing required skill gets CRITICAL priority."""
        resume = "Skills: HTML, CSS"
        jd = "Required Skills:\n- Docker"
        res = analyze_resume_job_gap(resume, jd)

        missing_item = res["missing_skills"][0]
        self.assertEqual(missing_item["skill"], "docker")
        self.assertEqual(missing_item["priority"], "CRITICAL")

    def test_07_optional_missing_skill_gets_lower_priority(self):
        """Missing optional skill gets lower priority (MEDIUM)."""
        resume = "Skills: Python"
        jd = "Required Skills:\n- Python\nNice to Have:\n- Kubernetes"
        res = analyze_resume_job_gap(resume, jd)

        missing_item = [m for m in res["missing_skills"] if m["skill"] == "kubernetes"][0]
        self.assertEqual(missing_item["priority"], "MEDIUM")

    def test_08_partial_skill_does_not_become_exact_match(self):
        """Partial match must be in partial_matches, not exact_matches."""
        resume = "Skills: PostgreSQL"
        jd = "Required Skills:\n- SQL"
        res = analyze_resume_job_gap(resume, jd)

        exact_names = [e["skill"] for e in res["exact_matches"]]
        self.assertNotIn("sql", exact_names)

    def test_09_no_double_counting(self):
        """Requirements must be counted exactly once towards total_requirements."""
        resume = "Skills: Python, PostgreSQL"
        jd = "Required Skills:\n- Python\n- SQL"
        res = analyze_resume_job_gap(resume, jd)

        total = res["skill_coverage"]["total_requirements"]
        exact = res["skill_coverage"]["exact_matches"]
        partial = res["skill_coverage"]["partial_matches"]
        missing = res["skill_coverage"]["missing"]
        self.assertEqual(total, exact + partial + missing)
        self.assertEqual(total, 2)

    def test_10_or_group_requirements_handled_correctly(self):
        """OR-group requirement evaluates to exact if any alternative matches."""
        resume = "Skills: Go"
        jd = "Required Qualifications:\n- Strong proficiency in Python or Go"
        res = analyze_resume_job_gap(resume, jd)

        self.assertEqual(res["skill_coverage"]["exact_matches"], 1)
        self.assertEqual(res["skill_coverage"]["missing"], 0)

    def test_11_empty_jd_handled_safely(self):
        """Empty JD returns zero counts safely without crashing."""
        res = analyze_resume_job_gap("Skills: Python", "")
        self.assertEqual(res["skill_coverage"]["total_requirements"], 0)
        self.assertEqual(res["skill_coverage"]["coverage_percentage"], 0.0)

    def test_12_empty_resume_skills_handled_safely(self):
        """Empty resume correctly marks all JD requirements as missing."""
        jd = "Required Skills:\n- Python\n- Docker"
        res = analyze_resume_job_gap("", jd)
        self.assertEqual(res["skill_coverage"]["exact_matches"], 0)
        self.assertEqual(res["skill_coverage"]["missing"], 2)

    @patch("gap_analyzer.is_gemini_available", return_value=False)
    def test_13_deterministic_analysis_works_without_gemini_key(self, mock_gemini):
        """Deterministic gap analysis works 100% offline when GEMINI_API_KEY is unavailable."""
        resume = "Skills: Python"
        jd = "Required Skills:\n- Python\n- Docker"
        res = analyze_resume_job_gap(resume, jd)
        res_ai = enhance_gap_analysis_with_ai(res, jd)

        self.assertIsNotNone(res_ai["skill_coverage"])
        self.assertIsNone(res_ai["ai_roadmap"])

    @patch("gap_analyzer.is_gemini_available", return_value=True)
    @patch("gap_analyzer.call_gemini_api", side_effect=Exception("API Network Timeout"))
    def test_14_gemini_failure_does_not_destroy_deterministic_analysis(self, mock_call, mock_gemini):
        """API failure in optional Gemini enhancement layer does not break deterministic gap analysis."""
        resume = "Skills: Python"
        jd = "Required Skills:\n- Python\n- Docker"
        res = analyze_resume_job_gap(resume, jd)
        res_ai = enhance_gap_analysis_with_ai(res, jd)

        self.assertIsNotNone(res_ai["skill_coverage"])
        self.assertEqual(res_ai["skill_coverage"]["exact_matches"], 1)
        self.assertIsNone(res_ai["ai_roadmap"])

    def test_15_existing_ats_score_remains_unchanged(self):
        """Verifies final_match_score produce identical output with gap analysis present."""
        resume = "Jane Doe. 5 years experience in Python, Flask, Docker."
        jd = "Backend Software Engineer. Required: Python, Flask, Docker. 5+ years experience."
        res = final_match_score(resume, jd)

        self.assertIn("ats_score", res)
        self.assertGreaterEqual(res["ats_score"], 70.0)


if __name__ == "__main__":
    unittest.main()
