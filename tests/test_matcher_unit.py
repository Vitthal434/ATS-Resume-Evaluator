"""
ResumeIQ — Stage 6.1 Core Matching Engine Unit Tests
Focuses on unit testing matcher.py and skills/ internal functions, edge cases,
boundary conditions, and contract structures without duplicate integration overhead.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from matcher import (
    extract_skills,
    extract_alternative_requirements,
    _extract_parenthetical_or_skills,
    extract_experience_requirements,
    experience_score,
    extract_education_requirements,
    calculate_skill_match,
    calculate_weighted_skill_score,
    final_match_score,
    preprocess,
)
from skills import SKILL_DATABASE, ALIAS_INDEX, _normalize_skill_database, _build_alias_index


class TestMatcherUnit(unittest.TestCase):
    """Focused unit tests for matcher.py logic and skills resolution."""

    # -----------------------------------------------------------------
    # 1. SKILL EXTRACTION UNIT TESTS
    # -----------------------------------------------------------------
    def test_extract_skills_special_characters(self):
        """Verify extraction of skills containing +, ., and -."""
        text = "Experienced in C++, Node.js, React.js, and Scikit-Learn."
        extracted = extract_skills(text)
        self.assertIn("c++", extracted)
        self.assertIn("node.js", extracted)
        self.assertIn("react", extracted)
        self.assertIn("scikit-learn", extracted)

    def test_extract_skills_overlapping_names(self):
        """Verify longer skill variants take precedence (e.g. javascript vs java)."""
        text = "Developers write JavaScript and Java code."
        extracted = extract_skills(text)
        self.assertIn("javascript", extracted)
        self.assertIn("java", extracted)

    def test_extract_skills_empty_or_no_match(self):
        """Verify empty strings or text without tech skills return empty set."""
        self.assertEqual(extract_skills(""), set())
        self.assertEqual(extract_skills("   "), set())
        self.assertEqual(extract_skills("Cooking, driving, and gardening."), set())

    # -----------------------------------------------------------------
    # 2. ALIAS & CANONICAL RESOLUTION UNIT TESTS
    # -----------------------------------------------------------------
    def test_alias_index_canonical_mapping(self):
        """Verify canonical skills and aliases map correctly in ALIAS_INDEX."""
        self.assertIn("python", SKILL_DATABASE)
        self.assertEqual(ALIAS_INDEX.get("py"), ["python"])
        self.assertEqual(ALIAS_INDEX.get("js"), ["javascript"])

    def test_alias_normalization_canonical_exclusion(self):
        """Verify canonical skill names are excluded from their own aliases list."""
        raw_db = {
            "test_skill": {
                "display": "Test Skill",
                "aliases": ["test_skill", "ts_alias"],
            }
        }
        norm = _normalize_skill_database(raw_db)
        self.assertEqual(norm["test_skill"]["aliases"], ["ts_alias"])

    # -----------------------------------------------------------------
    # 3. OR-GROUP & PARENTHETICAL HANDLING UNIT TESTS
    # -----------------------------------------------------------------
    def test_or_group_alternative_extraction(self):
        """Verify detection of alternative requirements separated by 'or' and '/'."""
        text1 = "Required skills: Python or Go for backend."
        alts1 = extract_alternative_requirements(text1)
        self.assertTrue(any(frozenset({"python", "go"}).issubset(s) for s in alts1))

        text2 = "Must know AWS / GCP for deployment."
        alts2 = extract_alternative_requirements(text2)
        self.assertTrue(any(frozenset({"aws", "gcp"}).issubset(s) for s in alts2))

    def test_parenthetical_or_descriptor_ignoring(self):
        """Verify parenthetical context inside OR conditions is detected."""
        text = "Required: React (JavaScript) or Vue."
        extracted = _extract_parenthetical_or_skills(text)
        self.assertIn("javascript", extracted)

    # -----------------------------------------------------------------
    # 4. EXPERIENCE EXTRACTION UNIT TESTS
    # -----------------------------------------------------------------
    def test_experience_extraction_regex(self):
        """Verify parsing of various experience formats."""
        self.assertEqual(extract_experience_requirements("Requires 5+ years of experience"), 5)
        self.assertEqual(extract_experience_requirements("Minimum of 3 years required"), 3)
        self.assertEqual(extract_experience_requirements("No explicit requirement"), 0)

    def test_experience_score_heuristics(self):
        """Verify experience scoring output ranges."""
        self.assertEqual(experience_score("5 years experience"), 100)
        self.assertEqual(experience_score("18 months experience"), 74)
        self.assertEqual(experience_score("Completed an internship and capstone project"), 65)
        self.assertEqual(experience_score("No experience mentioned"), 50)
        self.assertEqual(experience_score(""), 0)

    # -----------------------------------------------------------------
    # 5. EDUCATION EXTRACTION UNIT TESTS
    # -----------------------------------------------------------------
    def test_education_extraction_keyword_matching(self):
        """Verify degree keyword extraction from job text."""
        text_degree = "Requires a Bachelor degree in CS."
        edu_degree = extract_education_requirements(text_degree)
        self.assertIn("bachelor", edu_degree)

    # -----------------------------------------------------------------
    # 6. SCORE BOUNDARY & EDGE CASE UNIT TESTS
    # -----------------------------------------------------------------
    def test_weighted_skill_score_zero_total_weight(self):
        """Verify zero total job skill weight produces 0 score."""
        self.assertEqual(calculate_weighted_skill_score(set(), set(), set(), set(), [], [], []), 0)

    def test_calculate_skill_match_empty_inputs(self):
        """Verify skill match with empty inputs returns empty lists and 0 score."""
        score, matched, missing = calculate_skill_match("", "")
        self.assertEqual(score, 0)
        self.assertEqual(matched, [])
        self.assertEqual(missing, [])

    # -----------------------------------------------------------------
    # 7. FINAL MATCH SCORE CONTRACT STRUCTURE UNIT TESTS
    # -----------------------------------------------------------------
    def test_final_match_score_contract(self):
        """Verify output dictionary contract schema and value types."""
        res = final_match_score(
            "Python developer with Django and PostgreSQL experience.",
            "Backend Engineer. Required: Python, Django, PostgreSQL."
        )

        expected_keys = {
            "ats_score",
            "text_similarity",
            "skill_score",
            "experience_score",
            "matched_skills",
            "missing_skills",
            "recommendation",
            "suggestions",
        }
        self.assertEqual(set(res.keys()), expected_keys)
        self.assertIsInstance(res["ats_score"], float)
        self.assertIsInstance(res["text_similarity"], float)
        self.assertIsInstance(res["skill_score"], (int, float))
        self.assertIsInstance(res["experience_score"], (int, float))
        self.assertIsInstance(res["matched_skills"], list)
        self.assertIsInstance(res["missing_skills"], list)
        self.assertIsInstance(res["suggestions"], list)
        self.assertIn(res["recommendation"], ["Excellent Fit", "Good Fit", "Fair Fit", "Needs Improvement"])


if __name__ == "__main__":
    unittest.main()
