"""Job role recommendations based on matched resume skills."""

from skills import ALIAS_INDEX

JOB_DATABASE = {
    "AI Engineer": [
        "python",
        "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch",
        "numpy",
    ],
    "Data Scientist": [
        "python",
        "machine learning",
        "sql",
        "pandas",
        "numpy",
        "data science",
    ],
    "Machine Learning Engineer": [
        "python",
        "machine learning",
        "scikit-learn",
        "tensorflow",
        "pytorch",
        "git",
    ],
    "Data Analyst": [
        "sql",
        "excel",
        "power bi",
        "tableau",
        "python",
        "pandas",
    ],
    "Python Developer": [
        "python",
        "flask",
        "django",
        "mysql",
        "rest api",
        "git",
    ],
    "Frontend Developer": [
        "html",
        "css",
        "javascript",
        "react.js",
        "typescript",
        "git",
    ],
    "Backend Developer": [
        "python",
        "flask",
        "django",
        "sql",
        "mysql",
        "rest api",
    ],
    "Full Stack Developer": [
        "html",
        "css",
        "javascript",
        "react.js",
        "python",
        "flask",
        "mysql",
    ],
    "React Developer": [
        "javascript",
        "typescript",
        "react.js",
        "html",
        "css",
        "git",
    ],
    "Flask Developer": [
        "python",
        "flask",
        "rest api",
        "sql",
        "git",
    ],
    "Django Developer": [
        "python",
        "django",
        "rest api",
        "postgresql",
        "git",
    ],
    "Database Developer": [
        "sql",
        "mysql",
        "postgresql",
        "sqlite",
        "mongodb",
    ],
    "DevOps Engineer": [
        "aws",
        "docker",
        "kubernetes",
        "linux",
        "git",
    ],
    "Cloud Engineer": [
        "aws",
        "linux",
        "docker",
        "kubernetes",
        "rest api",
    ],
    "NLP Engineer": [
        "python",
        "natural language processing",
        "machine learning",
        "deep learning",
        "pytorch",
    ],
    "Computer Vision Engineer": [
        "python",
        "computer vision",
        "machine learning",
        "deep learning",
        "tensorflow",
    ],
}


# Pre-normalize JOB_DATABASE skills into canonical sets + alias lookup structures
PREPROCESSED_JOB_DATABASE = {}
for job_title, req_skills in JOB_DATABASE.items():
    req_matchers = []
    for skill in req_skills:
        req_s = skill.lower().strip()
        tokens = {req_s}
        if req_s in ALIAS_INDEX and ALIAS_INDEX[req_s]:
            tokens.update(ALIAS_INDEX[req_s])
        req_matchers.append((req_s, tokens))
    PREPROCESSED_JOB_DATABASE[job_title] = req_matchers


def recommend_jobs(resume_skills):
    """
    Return the top five deterministic job recommendations ranked by skill match score.
    Calculates match percentage against the distinct required skills of each role.
    """
    if not resume_skills:
        return [
            {"job": job, "score": 0}
            for job in list(JOB_DATABASE.keys())[:5]
        ]

    normalized_resume_skills = set()
    for skill in resume_skills:
        s = skill.lower().strip()
        normalized_resume_skills.add(s)
        if s in ALIAS_INDEX and ALIAS_INDEX[s]:
            normalized_resume_skills.update(ALIAS_INDEX[s])

    recommendations = []

    for job, req_matchers in PREPROCESSED_JOB_DATABASE.items():
        total_reqs = len(req_matchers)
        if total_reqs == 0:
            continue

        matched_count = 0
        for _canonical, acceptable_tokens in req_matchers:
            if not acceptable_tokens.isdisjoint(normalized_resume_skills):
                matched_count += 1

        score = round((matched_count / total_reqs) * 100)

        recommendations.append(
            {
                "job": job,
                "score": score,
                "matched_count": matched_count,
            }
        )

    recommendations.sort(
        key=lambda r: (
            r["score"],
            r["matched_count"],
        ),
        reverse=True,
    )

    top_recommendations = recommendations[:5]

    return [
        {
            "job": recommendation["job"],
            "score": recommendation["score"],
        }
        for recommendation in top_recommendations
    ]
