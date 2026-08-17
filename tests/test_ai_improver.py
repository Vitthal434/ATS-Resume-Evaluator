"""
ResumeIQ — Stage 9.1 AI Resume Improver Unit Tests
Tests AI endpoint routes, Gemini provider state checks, bullet extraction, and mock LLM response parsing.
Ensures zero real external API calls are made during automated test execution.
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

    @patch.dict(os.environ, {}, clear=True)
    def test_02_endpoint_missing_api_key(self):
        """POST /api/ai/improve when GEMINI_API_KEY is missing should return 503 Service Unavailable."""
        response = self.client.post(
            "/api/ai/improve",
            json={"resume_text": "Sample bullet text for Python engineer.", "job_description": "Python job."}
        )
        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertIn("GEMINI_API_KEY", data["error"])
        self.assertFalse(data["available"])

    @patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_test_key"})
    def test_03_endpoint_missing_payload_fields(self):
        """POST /api/ai/improve with missing resume_text or job_description should return 400 Bad Request."""
        response = self.client.post(
            "/api/ai/improve",
            json={"resume_text": "Only resume text."}
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Missing required fields", data["error"])

    @patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_test_key"})
    @patch("ai.resume_improver.call_gemini_api")
    def test_04_successful_ai_improvement(self, mock_gemini_call):
        """POST /api/ai/improve with valid input and mocked Gemini API response should return 200 OK."""
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
        mock_gemini_call.return_value = mock_response_json

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
        self.assertEqual(data["improvements"][0]["improved"], "Engineered scalable REST APIs using Python and Flask framework.")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_test_key"})
    @patch("ai.resume_improver.call_gemini_api")
    def test_05_ai_provider_failure_handling(self, mock_gemini_call):
        """POST /api/ai/improve when Gemini API call throws exception should return 500 error safely."""
        mock_gemini_call.side_effect = RuntimeError("Gemini API Network Error: Connection reset.")

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


if __name__ == "__main__":
    unittest.main()
