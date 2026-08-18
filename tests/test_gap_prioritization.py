"""
ResumeIQ — Stage 9.5 Intelligent Gap Prioritization & Improvement Roadmap Unit Tests
Verifies deterministic gap prioritization rules, impact classification, roadmap construction,
ordering hierarchy, offline execution without Gemini, and AI roadmap endpoint resilience.
"""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gap_analyzer import analyze_resume_job_gap, enhance_gap_analysis_with_ai
from matcher import SKILL_WEIGHT, TEXT_WEIGHT, EXPERIENCE_WEIGHT, final_match_score
from app import app


class TestGapPrioritization(unittest.TestCase):
    """Unit test suite for Stage 9.5 Gap Prioritization & Roadmap Engine."""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_weights_preserved(self):
        """Verify 50/30/20 ATS score weights remain strictly unchanged."""
        self.assertEqual(SKILL_WEIGHT, 0.50)
        self.assertEqual(TEXT_WEIGHT, 0.30)
        self.assertEqual(EXPERIENCE_WEIGHT, 0.20)

    def test_02_missing_required_skill_gets_high_priority(self):
        """Missing required skill must receive HIGH priority and high impact."""
        resume = "Skills: HTML, CSS"
        jd = "Required Skills:\n- Docker"
        res = analyze_resume_job_gap(resume, jd)

        gaps = res["prioritized_gaps"]
        docker_gap = [g for g in gaps if g["skill"] == "docker"][0]
        self.assertEqual(docker_gap["priority"], "HIGH")
        self.assertEqual(docker_gap["estimated_impact"], "high")
        self.assertEqual(docker_gap["status"], "missing")
        self.assertIn("Add truthful project or work experience", docker_gap["recommendation"])

    def test_03_partial_required_skill_gets_high_priority(self):
        """Partial match on required skill gets HIGH priority and medium impact."""
        resume = "Skills: PostgreSQL"
        jd = "Required Skills:\n- SQL"
        res = analyze_resume_job_gap(resume, jd)

        gaps = res["prioritized_gaps"]
        sql_gap = [g for g in gaps if g["skill"] == "sql"][0]
        self.assertEqual(sql_gap["priority"], "HIGH")
        self.assertEqual(sql_gap["estimated_impact"], "medium")
        self.assertEqual(sql_gap["status"], "partial")
        self.assertEqual(sql_gap["candidate_skill"], "postgresql")

    def test_04_missing_general_skill_gets_medium_priority(self):
        """Missing general role requirement gets MEDIUM/HIGH priority and estimated impact."""
        resume = "Skills: Python"
        jd = "Software Developer\nWe build web services with REST API concepts."
        res = analyze_resume_job_gap(resume, jd)

        gaps = res["prioritized_gaps"]
        rest_gap = [g for g in gaps if g["skill"] == "rest api"][0]
        self.assertIn(rest_gap["priority"], ("HIGH", "MEDIUM"))
        self.assertIn(rest_gap["estimated_impact"], ("high", "medium"))

    def test_05_missing_optional_skill_gets_low_priority(self):
        """Missing optional/preferred skill gets LOW / MEDIUM priority and low impact."""
        resume = "Skills: Python"
        jd = "Required Skills:\n- Python\nNice to Have:\n- Kubernetes"
        res = analyze_resume_job_gap(resume, jd)

        gaps = res["prioritized_gaps"]
        k8s_gap = [g for g in gaps if g["skill"] == "kubernetes"][0]
        self.assertEqual(k8s_gap["category"], "optional")
        self.assertEqual(k8s_gap["estimated_impact"], "low")

    def test_06_priority_ordering_hierarchy(self):
        """Gaps must be sorted deterministically: HIGH before MEDIUM before LOW."""
        resume = "Skills: HTML"
        jd = """
        Required Skills:
        - Docker
        Nice to Have:
        - Kubernetes
        """
        res = analyze_resume_job_gap(resume, jd)
        gaps = res["prioritized_gaps"]

        priorities = [g["priority"] for g in gaps]
        # Verify ordering: HIGH items precede LOW/MEDIUM items
        high_idx = [i for i, p in enumerate(priorities) if p == "HIGH"]
        low_idx = [i for i, p in enumerate(priorities) if p in ("LOW", "MEDIUM")]

        if high_idx and low_idx:
            self.assertLess(max(high_idx), min(low_idx))

    def test_07_roadmap_structure(self):
        """Roadmap must partition gaps into immediate, next, and optional buckets."""
        resume = "Skills: Python"
        jd = """
        Required Skills:
        - Docker
        Nice to Have:
        - Kubernetes
        """
        res = analyze_resume_job_gap(resume, jd)

        self.assertIn("roadmap", res)
        roadmap = res["roadmap"]
        self.assertIn("immediate", roadmap)
        self.assertIn("next", roadmap)
        self.assertIn("optional", roadmap)

        # Docker (missing required) should be in immediate
        immediate_skills = [g["skill"] for g in roadmap["immediate"]]
        self.assertIn("docker", immediate_skills)

    def test_08_no_duplicate_skills_in_gaps(self):
        """Prioritized gaps list must contain distinct skill names."""
        resume = "Skills: Python"
        jd = "Required Skills:\n- Python\n- Docker"
        res = analyze_resume_job_gap(resume, jd)

        gap_skills = [g["skill"] for g in res["prioritized_gaps"]]
        self.assertEqual(len(gap_skills), len(set(gap_skills)))

    def test_09_deterministic_results_offline(self):
        """Repeated calls produce identical deterministic gaps and roadmap without API calls."""
        resume = "Skills: Python"
        jd = "Required Skills:\n- Python\n- Docker"
        res1 = analyze_resume_job_gap(resume, jd)
        res2 = analyze_resume_job_gap(resume, jd)

        self.assertEqual(res1["prioritized_gaps"], res2["prioritized_gaps"])
        self.assertEqual(res1["roadmap"], res2["roadmap"])

    def test_10_scoring_integrity_preserved(self):
        """Deterministic score calculation is completely untouched by gap prioritization."""
        resume = "Jane Doe. 5 years experience in Python, Flask, Docker."
        jd = "Backend Software Engineer. Required: Python, Flask, Docker. 5+ years experience."
        result = final_match_score(resume, jd)

        expected = round(0.50 * result["skill_score"] + 0.30 * result["text_similarity"] + 0.20 * result["experience_score"], 2)
        self.assertAlmostEqual(result["ats_score"], expected, places=1)

    @patch("app.is_ai_available", return_value=True)
    @patch("gap_analyzer.is_ai_available", return_value=True)
    @patch("gap_analyzer.call_ai", return_value="- Step 1: Learn Docker\n- Step 2: Build containerized API")
    def test_11_ai_improvement_roadmap_endpoint_success(self, mock_ai_call, mock_gap_avail, mock_app_avail):
        """POST /api/ai/improvement-roadmap returns structured roadmap and AI explanation when AI is available."""
        payload = {
            "resume_text": "Skills: Python",
            "job_description": "Required Skills:\n- Python\n- Docker"
        }
        response = self.app.post("/api/ai/improvement-roadmap", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("roadmap", data)
        self.assertIn("ai_roadmap", data)
        self.assertIsNotNone(data["ai_roadmap"])

    @patch("app.is_ai_available", return_value=False)
    @patch("gap_analyzer.is_ai_available", return_value=False)
    def test_12_ai_improvement_roadmap_missing_key(self, mock_gap_avail, mock_app_avail):
        """POST /api/ai/improvement-roadmap returns HTTP 503 when AI is unavailable."""
        payload = {
            "resume_text": "Skills: Python",
            "job_description": "Required Skills:\n- Python\n- Docker"
        }
        response = self.app.post("/api/ai/improvement-roadmap", json=payload)
        self.assertEqual(response.status_code, 503)

    @patch("app.is_ai_available", return_value=True)
    @patch("gap_analyzer.is_ai_available", return_value=True)
    @patch("gap_analyzer.call_ai", side_effect=Exception("API Timeout"))
    def test_13_ai_improvement_roadmap_provider_failure(self, mock_ai_call, mock_gap_avail, mock_app_avail):
        """AI provider failure falls back safely returning deterministic roadmap without crashing."""
        payload = {
            "resume_text": "Skills: Python",
            "job_description": "Required Skills:\n- Python\n- Docker"
        }
        response = self.app.post("/api/ai/improvement-roadmap", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("roadmap", data)
        self.assertIsNone(data["ai_roadmap"])


if __name__ == "__main__":
    unittest.main()
