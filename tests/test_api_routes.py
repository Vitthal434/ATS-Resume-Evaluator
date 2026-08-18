"""
ResumeIQ — Stage 6.2 Flask Route Integration Tests
Tests HTTP endpoints ( / , /analyze, /match, /download-report ) using Flask's test_client.
Mocks external heavy PDF parsing and model inference to ensure fast, deterministic execution.
"""

import io
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


class TestApiRoutes(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_01_get_landing_page(self):
        """GET / should return 200 OK and render landing page."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ResumeIQ", response.data)

    def test_02_get_analyze_page(self):
        """GET /analyze should return 200 OK and render analyze page."""
        response = self.client.get("/analyze")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Ready to Analyze Your Resume?", response.data)

    @patch("app.read_pdf")
    @patch("app.final_match_score")
    @patch("app.generate_report")
    def test_03_post_match_valid_input(self, mock_report, mock_score, mock_read):
        """POST /match with valid resume file and JD should return 200 OK and dashboard HTML."""
        mock_read.return_value = "Python software engineer with 5 years experience."
        mock_score.return_value = {
            "ats_score": 85.0,
            "recommendation": "Excellent Fit",
            "skill_score": 90.0,
            "text_similarity": 60.0,
            "experience_score": 100.0,
            "matched_skills": ["python", "flask"],
            "missing_skills": ["docker"],
            "suggestions": ["Add Docker experience."],
        }
        mock_report.return_value = "reports/ATS_Report.pdf"

        dummy_pdf = (io.BytesIO(b"%PDF-1.4 dummy content"), "test_resume.pdf")

        response = self.client.post(
            "/match",
            data={
                "resume": dummy_pdf,
                "job_description": "Senior Python Engineer required.",
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Resume Health Overview", response.data)
        self.assertIn(b"85.0%", response.data)

    def test_04_post_match_missing_resume(self):
        """POST /match without resume file should return 400 Bad Request."""
        response = self.client.post(
            "/match",
            data={"job_description": "Senior Python Engineer required."},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_05_post_match_missing_jd(self):
        """POST /match without job description should return 400 Bad Request."""
        dummy_pdf = (io.BytesIO(b"%PDF-1.4 dummy content"), "test_resume.pdf")
        response = self.client.post(
            "/match",
            data={"resume": dummy_pdf},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_06_download_report_endpoint(self):
        """GET /download-report should return 200 OK when file exists or 404 when missing."""
        os.makedirs("reports", exist_ok=True)
        report_file = os.path.join("reports", "ATS_Report.pdf")

        created_dummy = False
        if not os.path.exists(report_file):
            with open(report_file, "wb") as f:
                f.write(b"%PDF-1.4 test report content")
            created_dummy = True

        try:
            response = self.client.get("/download-report")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, "application/pdf")
        finally:
            if created_dummy and os.path.exists(report_file):
                os.remove(report_file)

    @patch("app.read_docx")
    @patch("app.final_match_score")
    @patch("app.generate_report")
    def test_07_post_match_malformed_docx(self, mock_report, mock_score, mock_read_docx):
        """POST /match with docx file extension and empty text should handle safely."""
        mock_read_docx.return_value = ""
        mock_score.return_value = {
            "ats_score": 10.0,
            "recommendation": "Needs Improvement",
            "skill_score": 0.0,
            "text_similarity": 0.0,
            "experience_score": 0.0,
            "matched_skills": [],
            "missing_skills": ["python"],
            "suggestions": ["Upload a non-empty resume."],
        }
        mock_report.return_value = "reports/ATS_Report.pdf"

        dummy_docx = (io.BytesIO(b"malformed docx bytes"), "test_resume.docx")

        response = self.client.post(
            "/match",
            data={
                "resume": dummy_docx,
                "job_description": "Python developer required.",
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"10.0%", response.data)

    def test_08_get_health_endpoint(self):
        """GET /health should return 200 OK with JSON status ok."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
