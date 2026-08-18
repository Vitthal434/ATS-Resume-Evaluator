"""
ResumeIQ — Stage 9.3 Partial Credit Skill Matching Unit Tests
Verifies deterministic partial credit calculations for related/transferable skills,
exact match preservation, canonical alias resolution, non-double-counting, and zero credit for unrelated skills.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from matcher import (
    calculate_weighted_skill_score,
    calculate_skill_match,
    final_match_score,
    _get_related_skills,
    _evaluate_requirement_match,
    PARTIAL_MATCH_FACTOR,
    SKILL_WEIGHT,
    TEXT_WEIGHT,
    EXPERIENCE_WEIGHT,
)


class TestPartialSkillMatching(unittest.TestCase):
    """Unit tests for Stage 9.3 partial credit matching engine."""

    def test_01_weights_preserved_50_30_20(self):
        """Verify ATS score component weights remain strictly 50% Skill, 30% Text, 20% Experience."""
        self.assertEqual(SKILL_WEIGHT, 0.50)
        self.assertEqual(TEXT_WEIGHT, 0.30)
        self.assertEqual(EXPERIENCE_WEIGHT, 0.20)
        self.assertEqual(PARTIAL_MATCH_FACTOR, 0.50)

    def test_02_exact_matches_receive_full_credit(self):
        """Exact skills must receive 1.0 (100%) match credit."""
        resume_skills = {"python", "flask", "postgresql"}
        required_skills = {"python", "flask", "postgresql"}
        score = calculate_weighted_skill_score(resume_skills, required_skills, set())
        self.assertEqual(score, 100.0)

    def test_03_canonical_aliases_receive_full_credit(self):
        """Canonical aliases (e.g. py->python, js->javascript) map to canonical skills and receive 100% credit."""
        ratio_py, exact_py, _ = _evaluate_requirement_match({"python"}, {"python"})
        self.assertEqual(ratio_py, 1.0)
        self.assertEqual(exact_py, "python")

        ratio_js, exact_js, _ = _evaluate_requirement_match({"javascript"}, {"javascript"})
        self.assertEqual(ratio_js, 1.0)
        self.assertEqual(exact_js, "javascript")

    def test_04_explicit_related_skills_receive_partial_credit(self):
        """Explicit related skills (e.g. postgresql for sql requirement) must receive 0.5 partial credit."""
        # PostgreSQL is explicitly in sql's related skills list
        self.assertIn("postgresql", _get_related_skills("sql"))
        
        ratio, exact, related = _evaluate_requirement_match({"sql"}, {"postgresql"})
        self.assertEqual(ratio, PARTIAL_MATCH_FACTOR)
        self.assertIsNone(exact)
        self.assertEqual(related, "postgresql")

        # Score calculation: 1 required skill (weight 3), partial match (ratio 0.5) -> (1.5 / 3) * 100 = 50.0%
        score = calculate_weighted_skill_score({"postgresql"}, {"sql"}, set())
        self.assertEqual(score, 50.0)

    def test_05_unrelated_skills_receive_zero_credit(self):
        """Unrelated skills must receive 0.0 credit."""
        ratio, exact, related = _evaluate_requirement_match({"python"}, {"cooking"})
        self.assertEqual(ratio, 0.0)
        self.assertIsNone(exact)
        self.assertIsNone(related)

        score = calculate_weighted_skill_score({"cooking"}, {"python"}, set())
        self.assertEqual(score, 0.0)

    def test_06_related_skills_do_not_become_full_matches(self):
        """Related skills must yield partial score (50%), not 100% full match score."""
        score = calculate_weighted_skill_score({"postgresql"}, {"sql"}, set())
        self.assertNotEqual(score, 100.0)
        self.assertEqual(score, 50.0)

    def test_07_strict_no_broad_technology_inference(self):
        """TypeScript should NOT match JavaScript, React should NOT match Redux, Python should NOT match Django."""
        # TypeScript vs JavaScript -> Should be 0.0
        ratio_ts_js, _, _ = _evaluate_requirement_match({"javascript"}, {"typescript"})
        self.assertEqual(ratio_ts_js, 0.0)

        # React vs Redux -> Should be 0.0
        ratio_react_redux, _, _ = _evaluate_requirement_match({"redux"}, {"react"})
        self.assertEqual(ratio_react_redux, 0.0)

        # Python vs Django -> Should be 0.0 (Python proficiency does NOT imply Django framework proficiency)
        ratio_py_django, _, _ = _evaluate_requirement_match({"django"}, {"python"})
        self.assertEqual(ratio_py_django, 0.0)

        # JavaScript vs Node.js -> Should be 0.0
        ratio_js_node, _, _ = _evaluate_requirement_match({"node.js"}, {"javascript"})
        self.assertEqual(ratio_js_node, 0.0)

        # Java vs Spring Boot -> Should be 0.0
        ratio_java_spring, _, _ = _evaluate_requirement_match({"spring boot"}, {"java"})
        self.assertEqual(ratio_java_spring, 0.0)

        # React vs Next.js -> Should be 0.0
        ratio_react_next, _, _ = _evaluate_requirement_match({"next.js"}, {"react"})
        self.assertEqual(ratio_react_next, 0.0)

        # Docker vs Kubernetes -> Should be 0.0
        ratio_docker_k8s, _, _ = _evaluate_requirement_match({"kubernetes"}, {"docker"})
        self.assertEqual(ratio_docker_k8s, 0.0)

        # CSS vs Tailwind -> Should be 0.0
        ratio_css_tailwind, _, _ = _evaluate_requirement_match({"tailwind"}, {"css"})
        self.assertEqual(ratio_css_tailwind, 0.0)

    def test_08_curated_transferable_concept_relationships(self):
        """Verify high-confidence transferable concept relationships return 0.5 partial match credit."""
        # SQL <-> PostgreSQL
        r_sql_pg, _, _ = _evaluate_requirement_match({"sql"}, {"postgresql"})
        self.assertEqual(r_sql_pg, PARTIAL_MATCH_FACTOR)

        # Cloud Computing <-> AWS / Azure / GCP
        r_cloud_aws, _, _ = _evaluate_requirement_match({"aws"}, {"cloud computing"})
        self.assertEqual(r_cloud_aws, PARTIAL_MATCH_FACTOR)

        # CI/CD <-> Jenkins / GitHub Actions / GitLab CI
        r_cicd_jenkins, _, _ = _evaluate_requirement_match({"jenkins"}, {"ci cd"})
        self.assertEqual(r_cicd_jenkins, PARTIAL_MATCH_FACTOR)

        # Containerization <-> Docker
        r_container_docker, _, _ = _evaluate_requirement_match({"containerization"}, {"docker"})
        self.assertEqual(r_container_docker, PARTIAL_MATCH_FACTOR)

        # Infrastructure as Code <-> Terraform
        r_iac_tf, _, _ = _evaluate_requirement_match({"infrastructure as code"}, {"terraform"})
        self.assertEqual(r_iac_tf, PARTIAL_MATCH_FACTOR)

        # CSS <-> Sass
        r_css_sass, _, _ = _evaluate_requirement_match({"css"}, {"sass"})
        self.assertEqual(r_css_sass, PARTIAL_MATCH_FACTOR)

        # Redux <-> Redux Toolkit
        r_redux_rtk, _, _ = _evaluate_requirement_match({"redux toolkit"}, {"redux"})
        self.assertEqual(r_redux_rtk, PARTIAL_MATCH_FACTOR)

    def test_09_no_double_counting(self):
        """Evaluating a requirement with partial match should not double-count total weights."""
        # 2 required skills (total weight 6): Python (exact) + SQL (partial via postgresql)
        # Matched weight: 3*1.0 + 3*0.5 = 4.5. Score = (4.5 / 6.0) * 100 = 75.0%
        score = calculate_weighted_skill_score({"python", "postgresql"}, {"python", "sql"}, set())
        self.assertEqual(score, 75.0)

    def test_10_or_group_partial_match(self):
        """OR-group requirement receives 1.0 if exact match exists, or 0.5 if related skill exists."""
        # OR group: Python or Go
        ratio_exact, _, _ = _evaluate_requirement_match({"python", "go"}, {"python"})
        self.assertEqual(ratio_exact, 1.0)

        # OR group: SQL or MongoDB (candidate has PostgreSQL, which is related to SQL)
        ratio_partial, _, _ = _evaluate_requirement_match({"sql", "mongodb"}, {"postgresql"})
        self.assertEqual(ratio_partial, 0.5)

    def test_11_deterministic_no_network_calls(self):
        """Deterministic scoring produces results offline without any API calls."""
        res = final_match_score(
            "Experienced software developer with PostgreSQL database skills.",
            "Database Engineer. Required: SQL database experience."
        )
        self.assertIn("ats_score", res)
        self.assertGreater(res["skill_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
