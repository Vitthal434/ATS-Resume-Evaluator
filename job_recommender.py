"""Job role recommendations based on matched resume skills."""

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
        "api",
        "git",
    ],
    "Frontend Developer": [
        "html",
        "css",
        "javascript",
        "react",
        "typescript",
        "git",
    ],
    "Backend Developer": [
        "python",
        "flask",
        "django",
        "sql",
        "mysql",
        "api",
    ],
    "Full Stack Developer": [
        "html",
        "css",
        "javascript",
        "react",
        "python",
        "flask",
        "mysql",
    ],
    "React Developer": [
        "javascript",
        "typescript",
        "react",
        "html",
        "css",
        "git",
    ],
    "Flask Developer": [
        "python",
        "flask",
        "api",
        "sql",
        "git",
    ],
    "Django Developer": [
        "python",
        "django",
        "api",
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
        "api",
    ],
    "NLP Engineer": [
        "python",
        "nlp",
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


def recommend_jobs(resume_skills):
    """Return the top five job recommendations for the provided resume skills."""
    recommendations = []
    normalized_resume_skills = set(skill.lower() for skill in resume_skills)

    for job, required_skills in JOB_DATABASE.items():
        normalized_required_skills = set(skill.lower() for skill in required_skills)
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

    for recommendation in recommendations:
        recommendation.pop("matched_count")

    return recommendations[:5]
