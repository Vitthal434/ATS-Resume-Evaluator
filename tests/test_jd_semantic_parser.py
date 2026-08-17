"""
ResumeIQ — Stage 9.2 / Stage 10A Semantic Job Description Parser Unit Tests
Tests structured JD parsing, fallback handling, schema validation, and API endpoints.
Mocks AI provider calls to ensure zero real network calls or model loads during testing.

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
from ai.jd_semantic_parser import parse_job_description, validate_semantic_schema, _get_empty_schema
from matcher import final_match_score


class TestJdSemanticParser(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_01_schema_validation_empty_input(self):
        """validate_semantic_schema should return default valid schema on empty/malformed dict."""
        validated = validate_semantic_schema({})
        self.assertEqual(validated["job_title"], "Software Engineering Role")
        self.assertIsInstance(validated["required_skills"], list)
        self.assertIsInstance(validated["alternative_requirements"], list)

    @patch("ai.jd_semantic_parser.is_ai_available", return_value=False)
    def test_02_parse_jd_provider_unavailable(self, mock_avail):
        """parse_job_description when provider is unavailable should return fallback structure."""
        res = parse_job_description("Senior Python Engineer with 3+ years experience.")
        self.assertFalse(res["available"])
        self.assertIsInstance(res["error"], str)
        self.assertGreater(len(res["error"]), 0)
        self.assertEqual(res["analysis"]["job_title"], "Software Engineering Role")

    @patch("app.is_ai_available", return_value=False)
    def test_03_endpoint_ai_unavailable_returns_503(self, mock_avail):
        """POST /api/ai/parse-jd when provider is unavailable should return 503."""
        response = self.client.post(
            "/api/ai/parse-jd",
            json={"job_description": "Senior Backend Developer required."}
        )
        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertIn("not available", data["error"].lower())

    @patch("app.is_ai_available", return_value=True)
    def test_04_endpoint_missing_jd_field(self, mock_avail):
        """POST /api/ai/parse-jd without job_description should return 400 Bad Request."""
        response = self.client.post(
            "/api/ai/parse-jd",
            json={}
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Job description is required", data["error"])

    @patch("app.is_ai_available", return_value=True)
    @patch("ai.jd_semantic_parser.call_ai")
    def test_05_successful_jd_parsing(self, mock_call_ai, mock_avail):
        """POST /api/ai/parse-jd with mocked AI response should return 200 OK with analysis."""
        mock_output = {
            "job_title": "Senior Backend Developer",
            "required_skills": [
                {"skill": "python", "importance": "required", "evidence": "Must have Python experience"}
            ],
            "alternative_requirements": [
                {"group": ["python", "go"], "requirement_type": "required"}
            ],
            "preferred_skills": [
                {"skill": "docker", "importance": "preferred", "evidence": "Docker is nice to have"}
            ],
            "responsibilities": ["Design scalable backend microservices."],
            "experience_requirements": [
                {"requirement": "3+ years backend experience", "years": 3, "domain": "backend development"}
            ],
            "education_requirements": ["BS in Computer Science"],
            "certifications": [],
            "tools_and_platforms": ["AWS", "Docker"],
            "domain_knowledge": ["distributed systems"],
            "soft_skills": ["communication"]
        }
        mock_call_ai.return_value = json.dumps(mock_output)

        response = self.client.post(
            "/api/ai/parse-jd",
            json={"job_description": "Senior Backend Developer. 3+ years experience with Python or Go."}
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        analysis = data["analysis"]
        self.assertEqual(analysis["job_title"], "Senior Backend Developer")
        self.assertEqual(len(analysis["required_skills"]), 1)
        self.assertEqual(analysis["required_skills"][0]["skill"], "python")
        self.assertEqual(analysis["alternative_requirements"][0]["group"], ["python", "go"])

    @patch("app.is_ai_available", return_value=True)
    @patch("ai.jd_semantic_parser.call_ai")
    def test_06_malformed_json_handling(self, mock_call_ai, mock_avail):
        """POST /api/ai/parse-jd when AI returns invalid JSON should return 500 error safely."""
        mock_call_ai.return_value = "invalid raw text non-json response"

        response = self.client.post(
            "/api/ai/parse-jd",
            json={"job_description": "Senior Backend Developer."}
        )

        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("Unable to semantically parse job description", data["error"])

    @patch("app.is_ai_available", return_value=True)
    @patch("ai.jd_semantic_parser.call_ai")
    def test_07_provider_failure_returns_500(self, mock_call_ai, mock_avail):
        """POST /api/ai/parse-jd when AI call throws exception should return 500 error."""
        mock_call_ai.side_effect = RuntimeError("Local model load timeout.")

        response = self.client.post(
            "/api/ai/parse-jd",
            json={"job_description": "Senior Backend Developer."}
        )

        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("Unable to semantically parse job description", data["error"])

    def test_08_deterministic_scoring_unaffected(self):
        """Verify that deterministic ATS score calculations remain 100% unchanged."""
        resume = "Python software engineer with 5 years experience in Flask, Docker, and PostgreSQL."
        jd = "Senior Python Developer required with Flask, Docker, PostgreSQL experience."

        result = final_match_score(resume, jd)
        self.assertIn("ats_score", result)
        self.assertGreater(result["ats_score"], 80.0)
        self.assertEqual(result["skill_score"], 100.0)


if __name__ == "__main__":
    unittest.main()
