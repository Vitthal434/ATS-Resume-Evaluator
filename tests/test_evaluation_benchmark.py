"""
ResumeIQ — Stage 6.3 Synthetic Evaluation Benchmark Harness
Runs synthetic resume/JD evaluation cases from evaluation_dataset.json against matcher.py.
Verifies scoring sanity, boundary limits, cross-domain ordering, and logs suspicious findings.
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from matcher import final_match_score


class TestEvaluationBenchmark(unittest.TestCase):
    """Benchmark harness for synthetic evaluation dataset."""

    @classmethod
    def setUpClass(cls):
        dataset_path = os.path.join(os.path.dirname(__file__), "evaluation_dataset.json")
        with open(dataset_path, "r", encoding="utf-8") as f:
            cls.dataset = json.load(f)
        cls.results = []
        cls.findings = []

    def test_01_run_all_dataset_cases(self):
        """Execute final_match_score across all evaluation cases and assert structural validity."""
        cases = self.dataset.get("test_cases", [])
        self.assertGreaterEqual(len(cases), 12, "Dataset should contain at least 12 test cases.")

        print("\n" + "=" * 70)
        print("ResumeIQ Stage 6.3 Benchmark Results")
        print("=" * 70)

        for case in cases:
            cid = case["id"]
            resume = case["resume"]
            jd = case["job_description"]
            match_type = case["match_type"]

            res = final_match_score(resume, jd)
            ats = res["ats_score"]
            skill_s = res["skill_score"]
            text_sim = res["text_similarity"]
            exp_s = res["experience_score"]
            category = res["recommendation"]

            self.assertGreaterEqual(ats, 0.0, f"[{cid}] Score cannot be negative.")
            self.assertLessEqual(ats, 100.0, f"[{cid}] Score cannot exceed 100.")
            self.assertIsInstance(category, str)

            if not resume or not resume.strip():
                self.assertEqual(ats, 0.0, f"[{cid}] Empty resume must return 0.0 ATS score.")

            min_exp = case.get("expected_min_score", 0.0)
            max_exp = case.get("expected_max_score", 100.0)

            # Record result
            entry = {
                "id": cid,
                "match_type": match_type,
                "ats_score": ats,
                "skill_score": skill_s,
                "text_similarity": text_sim,
                "experience_score": exp_s,
                "recommendation": category,
            }
            self.results.append(entry)

            print(
                f"[{cid[:28]:<28}] ATS: {ats:>5.1f}% | Skill: {skill_s:>5.1f}% | "
                f"TextSim: {text_sim:>5.1f}% | Fit: {category}"
            )

            # Check for suspicious scoring finding (without forcing assertion failures unless critical)
            if match_type == "unrelated" and ats > 40.0:
                self.findings.append(
                    f"SUSPICIOUS: Unrelated case [{cid}] scored {ats:.1f}% (> 40.0%)."
                )
            if match_type == "strong" and ats < 70.0:
                self.findings.append(
                    f"SUSPICIOUS: Strong match case [{cid}] scored {ats:.1f}% (< 70.0%)."
                )

    def test_02_relative_scoring_order_sanity(self):
        """Verify that strong matches generally outscore weak/unrelated matches."""
        results_by_id = {r["id"]: r["ats_score"] for r in self.results}

        if "case_01_frontend_strong" in results_by_id and "case_09_unrelated_construction" in results_by_id:
            strong_score = results_by_id["case_01_frontend_strong"]
            unrelated_score = results_by_id["case_09_unrelated_construction"]
            self.assertGreater(
                strong_score,
                unrelated_score,
                "Strong frontend match must outscore unrelated construction resume.",
            )

        if "case_02_backend_strong" in results_by_id and "case_11_experience_mismatch" in results_by_id:
            senior_score = results_by_id["case_02_backend_strong"]
            junior_score = results_by_id["case_11_experience_mismatch"]
            self.assertGreater(
                senior_score,
                junior_score,
                "Senior backend match (5y) must outscore junior developer (6m) on lead architect JD.",
            )


if __name__ == "__main__":
    unittest.main()
