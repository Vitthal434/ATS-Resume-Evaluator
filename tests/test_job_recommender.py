"""
ResumeIQ — Job Recommender Unit Tests
Verifies deterministic skill-based job role recommendations:
  - Different resume skill profiles produce distinct role rankings
  - Same resume produces identical, deterministic rankings
  - Canonical aliases properly resolve
  - Irrelevant roles rank lower
  - Empty skill sets handle safely without errors
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from job_recommender import recommend_jobs


class TestJobRecommender(unittest.TestCase):
    def test_01_frontend_skills_recommend_frontend_roles(self):
        """Frontend skills should recommend Frontend Developer and React Developer."""
        skills = ["javascript", "typescript", "react.js", "html", "css", "git"]
        recs = recommend_jobs(skills)
        jobs = [r["job"] for r in recs]
        self.assertIn("Frontend Developer", jobs)
        self.assertIn("React Developer", jobs)
        top_job = recs[0]
        self.assertIn(top_job["job"], ["Frontend Developer", "React Developer"])
        self.assertEqual(top_job["score"], 100)

    def test_02_backend_skills_recommend_backend_roles(self):
        """Backend skills should recommend Backend, Python, or Django Developer."""
        skills = ["python", "django", "postgresql", "rest api", "git"]
        recs = recommend_jobs(skills)
        jobs = [r["job"] for r in recs]
        self.assertIn("Django Developer", jobs)
        self.assertIn("Backend Developer", jobs)
        self.assertNotIn("Frontend Developer", jobs[:2])

    def test_03_ml_skills_recommend_ml_ai_roles(self):
        """ML skills should recommend ML Engineer, AI Engineer, or Data Scientist."""
        skills = ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "numpy"]
        recs = recommend_jobs(skills)
        jobs = [r["job"] for r in recs]
        self.assertIn("AI Engineer", jobs)
        self.assertIn("Machine Learning Engineer", jobs)
        self.assertNotIn("Frontend Developer", jobs[:3])

    def test_04_devops_skills_recommend_devops_cloud_roles(self):
        """DevOps skills should recommend DevOps Engineer or Cloud Engineer."""
        skills = ["aws", "docker", "kubernetes", "linux", "git"]
        recs = recommend_jobs(skills)
        jobs = [r["job"] for r in recs]
        self.assertIn("DevOps Engineer", jobs)
        top_job = recs[0]
        self.assertEqual(top_job["job"], "DevOps Engineer")
        self.assertEqual(top_job["score"], 100)

    def test_05_alias_support_in_recommender(self):
        """Aliases (py, js, ts, k8s) should match their canonical equivalents."""
        skills = ["py", "django", "rest api", "postgres", "git"]
        recs = recommend_jobs(skills)
        jobs = [r["job"] for r in recs]
        self.assertIn("Django Developer", jobs)
        top_score = recs[0]["score"]
        self.assertGreaterEqual(top_score, 80)

    def test_06_deterministic_stability(self):
        """Same input skills should produce identical results across multiple calls."""
        skills = ["python", "flask", "sql", "git"]
        run1 = recommend_jobs(skills)
        run2 = recommend_jobs(skills)
        run3 = recommend_jobs(skills)
        self.assertEqual(run1, run2)
        self.assertEqual(run2, run3)

    def test_07_empty_skills_safe_return(self):
        """Empty input skills should return 5 roles with 0% score and not crash."""
        recs = recommend_jobs([])
        self.assertEqual(len(recs), 5)
        for r in recs:
            self.assertEqual(r["score"], 0)

    def test_08_none_skills_safe_return(self):
        """None input skills should return 5 roles with 0% score and not crash."""
        recs = recommend_jobs(None)
        self.assertEqual(len(recs), 5)
        for r in recs:
            self.assertEqual(r["score"], 0)


if __name__ == "__main__":
    unittest.main()
