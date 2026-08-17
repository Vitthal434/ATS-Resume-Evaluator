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


# Pre-normalize JOB_DATABASE skills once at module load time
PREPROCESSED_JOB_DATABASE = {}
for job_title, req_skills in JOB_DATABASE.items():
    norm_set = set()
    for skill in req_skills:
        req_s = skill.lower().strip()
        norm_set.add(req_s)
        if req_s in ALIAS_INDEX and ALIAS_INDEX[req_s]:
            norm_set.update(ALIAS_INDEX[req_s])
    PREPROCESSED_JOB_DATABASE[job_title] = norm_set


def recommend_jobs(resume_skills):
    """Return the top five job recommendations for the provided resume skills."""
    normalized_resume_skills = set()
    for skill in resume_skills:
        s = skill.lower().strip()
        normalized_resume_skills.add(s)
        if s in ALIAS_INDEX and ALIAS_INDEX[s]:
            normalized_resume_skills.update(ALIAS_INDEX[s])

    recommendations = []

    for job, normalized_required_skills in PREPROCESSED_JOB_DATABASE.items():
        matched_skills = normalized_resume_skills.intersection(
            normalized_required_skills
        )
        score = round((len(matched_skills) / len(normalized_required_skills)) * 100)

        recommendations.append(
            {
                "job": job,
                "score": score,
                "matched_count": len(matched_skills),
            }
        )

    recommendations.sort(
        key=lambda recommendation: (
            recommendation["score"],
            recommendation["matched_count"],
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
