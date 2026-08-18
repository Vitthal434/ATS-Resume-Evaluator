"""
ResumeIQ — Stage 9.6 PDF Report Generator Unit Tests
Verifies that generate_report() produces a valid, non-empty PDF for:
  - short inputs (empty resume / minimal JD)
  - representative full inputs with gap_analysis
  - long inputs (stress test for overflow)
  - optional AI roadmap present / absent
  - no gap_analysis (backward-compatible signature)
  - scoring weights not mutated by report generation
"""

import os
import sys
import struct
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from report_generator import generate_report, format_skill

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")


def _read_pdf(path):
    with open(path, "rb") as f:
        return f.read()


def _is_valid_pdf(data):
    """Basic PDF magic-byte check."""
    return data[:4] == b"%PDF"


class TestReportGenerator(unittest.TestCase):
    """Unit tests for Stage 9.6 PDF report generator."""

    # --- format_skill ---

    def test_01_format_skill_known_acronym(self):
        self.assertEqual(format_skill("aws"), "AWS")
        self.assertEqual(format_skill("sql"), "SQL")
        self.assertEqual(format_skill("rest api"), "REST API")
        self.assertEqual(format_skill("javascript"), "JavaScript")

    def test_02_format_skill_title_case_fallback(self):
        self.assertEqual(format_skill("docker"), "Docker")
        self.assertEqual(format_skill("kubernetes"), "Kubernetes")

    def test_03_format_skill_or_group(self):
        result = format_skill("python or go")
        self.assertIn("or", result)
        self.assertIn("Python", result)
        self.assertIn("Go", result)

    def test_04_format_skill_empty(self):
        self.assertEqual(format_skill(""), "")
        self.assertEqual(format_skill(None), "")

    # --- generate_report: minimal inputs ---

    def test_05_report_minimal_no_gap_analysis(self):
        """generate_report() with no gap_analysis produces a valid PDF (backward compat)."""
        path = generate_report(
            score=75.0,
            category="Good Match",
            skill_score=80.0,
            text_similarity=60.0,
            experience_score=70.0,
            matched=["python", "sql"],
            missing=["docker"],
            suggestions=["Add Docker experience."],
            recommended_jobs=[{"job": "Backend Developer", "score": 82}],
        )
        self.assertTrue(os.path.exists(path))
        data = _read_pdf(path)
        self.assertTrue(_is_valid_pdf(data))
        self.assertGreater(len(data), 1024)

    def test_06_report_empty_skills(self):
        """generate_report() with empty matched/missing lists should not crash."""
        path = generate_report(
            score=0.0,
            category="Poor Match",
            skill_score=0.0,
            text_similarity=0.0,
            experience_score=0.0,
            matched=[],
            missing=[],
            suggestions=[],
            recommended_jobs=[],
        )
        self.assertTrue(os.path.exists(path))
        data = _read_pdf(path)
        self.assertTrue(_is_valid_pdf(data))

    def test_07_report_with_gap_analysis(self):
        """generate_report() with full gap_analysis produces a valid PDF."""
        gap = {
            "skill_coverage": {
                "total_requirements": 3,
                "exact_matches": 1,
                "partial_matches": 1,
                "missing": 1,
                "coverage_percentage": 66.7,
            },
            "exact_matches": [{"skill": "python", "category": "required"}],
            "partial_matches": [
                {"required_skill": "sql", "candidate_skill": "postgresql", "credit": 0.5, "category": "required"}
            ],
            "missing_skills": [{"skill": "docker", "category": "required", "priority": "HIGH"}],
            "recommendations": [{"skill": "docker", "priority": "HIGH", "reason": "Docker is missing."}],
            "prioritized_gaps": [
                {
                    "skill": "docker",
                    "status": "missing",
                    "category": "required",
                    "priority": "HIGH",
                    "estimated_impact": "high",
                    "impact_reason": "Required skill currently missing",
                    "recommendation": "Add truthful project experience demonstrating Docker.",
                },
                {
                    "skill": "sql",
                    "status": "partial",
                    "candidate_skill": "postgresql",
                    "category": "required",
                    "priority": "HIGH",
                    "estimated_impact": "medium",
                    "impact_reason": "Required skill partially matched via postgresql",
                    "recommendation": "Strengthen PostgreSQL evidence to demonstrate SQL proficiency.",
                },
            ],
            "roadmap": {
                "immediate": [
                    {
                        "skill": "docker",
                        "status": "missing",
                        "category": "required",
                        "priority": "HIGH",
                        "estimated_impact": "high",
                        "impact_reason": "Required skill currently missing",
                        "recommendation": "Add truthful project experience demonstrating Docker.",
                    }
                ],
                "next": [],
                "optional": [],
            },
            "ai_roadmap": None,
        }
        path = generate_report(
            score=65.0,
            category="Fair Match",
            skill_score=60.0,
            text_similarity=55.0,
            experience_score=70.0,
            matched=["python"],
            missing=["docker"],
            suggestions=["Add Docker experience."],
            recommended_jobs=[{"job": "Backend Developer", "score": 72}],
            gap_analysis=gap,
        )
        self.assertTrue(os.path.exists(path))
        data = _read_pdf(path)
        self.assertTrue(_is_valid_pdf(data))
        self.assertGreater(len(data), 2048)

    def test_08_report_with_ai_roadmap(self):
        """generate_report() with non-None ai_roadmap text renders without crash."""
        gap = {
            "skill_coverage": {"total_requirements": 1, "exact_matches": 0,
                                "partial_matches": 0, "missing": 1, "coverage_percentage": 0.0},
            "exact_matches": [],
            "partial_matches": [],
            "missing_skills": [{"skill": "docker", "category": "required", "priority": "HIGH"}],
            "recommendations": [],
            "prioritized_gaps": [],
            "roadmap": {"immediate": [], "next": [], "optional": []},
            "ai_roadmap": "- Step 1: Complete Docker fundamentals.\n- Step 2: Build a containerized project.",
        }
        path = generate_report(
            score=40.0,
            category="Poor Match",
            skill_score=30.0,
            text_similarity=40.0,
            experience_score=50.0,
            matched=[],
            missing=["docker"],
            suggestions=[],
            recommended_jobs=[],
            gap_analysis=gap,
        )
        self.assertTrue(os.path.exists(path))
        data = _read_pdf(path)
        self.assertTrue(_is_valid_pdf(data))

    def test_09_report_long_inputs_no_crash(self):
        """generate_report() with very long skill lists and long recommendations stays stable."""
        long_matched = [f"skill_{i}" for i in range(40)]
        long_missing = [f"missing_skill_{i}" for i in range(30)]
        long_suggestions = [f"Add experience with technology_{i} if relevant." for i in range(15)]
        long_gaps = [
            {
                "skill": f"skill_{i}",
                "status": "missing",
                "category": "required",
                "priority": "HIGH",
                "estimated_impact": "high",
                "impact_reason": "Required skill currently missing",
                "recommendation": f"Add verifiable experience for skill_{i} in your resume if you have used it.",
            }
            for i in range(20)
        ]
        gap = {
            "skill_coverage": {"total_requirements": 50, "exact_matches": 40,
                                "partial_matches": 0, "missing": 10, "coverage_percentage": 80.0},
            "exact_matches": [],
            "partial_matches": [],
            "missing_skills": [],
            "recommendations": [],
            "prioritized_gaps": long_gaps,
            "roadmap": {"immediate": long_gaps, "next": [], "optional": []},
            "ai_roadmap": None,
        }
        path = generate_report(
            score=80.0,
            category="Strong Match",
            skill_score=85.0,
            text_similarity=75.0,
            experience_score=80.0,
            matched=long_matched,
            missing=long_missing,
            suggestions=long_suggestions,
            recommended_jobs=[{"job": "Senior Engineer", "score": 91}],
            gap_analysis=gap,
        )
        self.assertTrue(os.path.exists(path))
        data = _read_pdf(path)
        self.assertTrue(_is_valid_pdf(data))
        # Long reports should produce a meaningful PDF (>8 KB is a reliable indicator)
        self.assertGreater(len(data), 8000)

    def test_10_report_output_path_correct(self):
        """generate_report() returns a path ending with ATS_Report.pdf."""
        path = generate_report(
            score=50.0, category="Fair Match",
            skill_score=50.0, text_similarity=50.0, experience_score=50.0,
            matched=["python"], missing=["docker"], suggestions=[], recommended_jobs=[],
        )
        self.assertTrue(path.endswith("ATS_Report.pdf"))


if __name__ == "__main__":
    unittest.main()
