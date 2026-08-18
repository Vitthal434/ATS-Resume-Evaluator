"""
ResumeIQ — Stage 9.1 / Stage 10A AI Resume Improver Unit Tests
Tests AI endpoint routes, provider state checks, bullet extraction, and mock LLM response parsing.
Ensures zero real external API calls or model loads are made during automated test execution.

Updated in Stage 10A to mock ai.provider abstraction (call_ai / is_ai_available)
instead of the Gemini-specific call_gemini_api.
"""

import json
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from ai.resume_improver import extract_bullets, improve_resume_bullets


class TestAiImprover(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_01_extract_bullets(self):
        """extract_bullets should extract bullet lines between 25 and 300 characters."""
        raw_text = """
        John Doe Resume
        - Developed REST APIs using Python and Flask framework.
        * Built interactive web dashboards with JavaScript and React.
        Too short.
        """
        bullets = extract_bullets(raw_text)
        self.assertGreaterEqual(len(bullets), 2)
        self.assertIn("Developed REST APIs using Python and Flask framework.", bullets[0])

    @patch("app.is_ai_available", return_value=False)
    def test_02_endpoint_ai_unavailable_returns_503(self, mock_avail):
        """POST /api/ai/improve when AI provider is unavailable should return 503."""
        response = self.client.post(
            "/api/ai/improve",
            json={"resume_text": "Sample bullet text for Python engineer.", "job_description": "Python job."}
        )
        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertFalse(data["available"])

    @patch("app.is_ai_available", return_value=True)
    def test_03_endpoint_missing_payload_fields(self, mock_avail):
        """POST /api/ai/improve with missing resume_text or job_description should return 400 Bad Request."""
        response = self.client.post(
            "/api/ai/improve",
            json={"resume_text": "Only resume text."}
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Missing required fields", data["error"])

    @patch("app.is_ai_available", return_value=True)
    @patch("ai.resume_improver.call_ai")
    def test_04_successful_ai_improvement(self, mock_call_ai, mock_avail):
        """POST /api/ai/improve with valid input and mocked AI response should return 200 OK."""
        mock_response_json = json.dumps({
            "improvements": [
                {
                    "original": "Developed web applications using Python and Flask framework.",
                    "improved": "Engineered scalable REST APIs using Python and Flask framework.",
                    "reason": "Uses stronger action verb and technical context.",
                    "keywords_added": ["REST APIs", "scalable"],
                    "skills_referenced": ["python", "flask"],
                    "impact_level": "High",
                    "confidence": 0.95
                }
            ]
        })
        mock_call_ai.return_value = mock_response_json

        response = self.client.post(
            "/api/ai/improve",
            json={
                "resume_text": "- Developed web applications using Python and Flask framework.",
                "job_description": "Senior Python Developer with REST API experience required.",
                "missing_skills": ["docker"]
            }
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["available"])
        self.assertEqual(len(data["improvements"]), 1)
        self.assertEqual(
            data["improvements"][0]["improved"],
            "Engineered scalable REST APIs using Python and Flask framework."
        )

    @patch("app.is_ai_available", return_value=True)
    @patch("ai.resume_improver.call_ai")
    def test_05_ai_provider_failure_handling(self, mock_call_ai, mock_avail):
        """POST /api/ai/improve when AI call throws exception should return 500 error safely."""
        mock_call_ai.side_effect = RuntimeError("Local model load failed: Connection reset.")

        response = self.client.post(
            "/api/ai/improve",
            json={
                "resume_text": "- Developed web applications using Python and Flask framework.",
                "job_description": "Senior Python Developer required."
            }
        )

        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("Connection reset", data["error"])

    def test_06_improve_bullets_unavailable_returns_dict(self):
        """improve_resume_bullets returns error dict (not exception) when provider unavailable."""
        with patch("ai.resume_improver.is_ai_available", return_value=False):
            result = improve_resume_bullets(
                "- Built REST APIs with Python. Delivered 3 production services.",
                "Senior Python Developer needed."
            )
        self.assertFalse(result["available"])
        self.assertIsInstance(result["error"], str)
        self.assertEqual(result["improvements"], [])

    @patch("ai.resume_improver.is_ai_available", return_value=True)
    @patch("ai.resume_improver.call_ai", return_value='{"improvements": []}')
    def test_07_improve_bullets_empty_improvements(self, mock_call, mock_avail):
        """improve_resume_bullets handles model returning empty improvements list."""
        result = improve_resume_bullets(
            "- Built REST APIs with Python and Flask. Delivered production services.",
            "Senior Python Developer required."
        )
        self.assertTrue(result["available"])
        self.assertIsNone(result["error"])
        self.assertEqual(result["improvements"], [])

    @patch("ai.resume_improver.is_ai_available", return_value=True)
    @patch("ai.resume_improver.call_ai", return_value="This is not JSON at all.")
    def test_08_improve_bullets_malformed_json(self, mock_call, mock_avail):
        """improve_resume_bullets returns JSON parse error dict on malformed response."""
        result = improve_resume_bullets(
            "- Built REST APIs with Python and Flask. Delivered production services.",
            "Senior Python Developer required."
        )
        self.assertTrue(result["available"])
        self.assertIsNotNone(result["error"])
        self.assertIn("JSON", result["error"])
        self.assertEqual(result["improvements"], [])


if __name__ == "__main__":
    unittest.main()
