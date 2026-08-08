import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILL_WEIGHT = 0.50
TEXT_WEIGHT = 0.30
EXPERIENCE_WEIGHT = 0.20

SKILL_CATEGORIES = {
    "programming_languages": {
        "python",
        "java",
        "c",
        "c++",
        "javascript",
        "typescript",
        "go",
    },
    "frontend": {
        "html",
        "css",
        "bootstrap",
        "tailwind",
        "react",
        "angular",
        "vue",
    },
    "backend": {
        "flask",
        "django",
        "fastapi",
        "node.js",
        "express",
        "rest api",
        "grpc",
    },
    "databases": {
        "sql",
        "mysql",
        "postgresql",
        "mongodb",
        "sqlite",
        "redis",
        "dynamodb",
        "pinecone",
        "qdrant",
        "chromadb",
    },
    "ai_ml": {
        "machine learning",
        "deep learning",
        "data science",
        "artificial intelligence",
        "nlp",
        "computer vision",
        "transformers",
        "bert",
        "llama",
        "mistral",
        "rag",
        "prompt engineering",
        "natural language processing",
    },
    "python_libraries": {
        "numpy",
        "pandas",
        "matplotlib",
        "seaborn",
        "scikit-learn",
        "tensorflow",
        "keras",
        "pytorch",
    },
    "data_analytics": {
        "power bi",
        "tableau",
        "excel",
    },
    "cloud_devops": {
        "aws",
        "gcp",
        "azure",
        "docker",
        "kubernetes",
        "redis",
        "terraform",
        "cloudformation",
        "mlflow",
        "kubeflow",
        "triton inference server",
    },
    "version_control": {
        "git",
        "github",
    },
    "operating_systems": {
        "linux",
    },
    "soft_skills": {
        "communication",
        "leadership",
        "problem solving",
        "teamwork",
        "critical thinking",
    },
    "other": {
        "oop",
        "dsa",
    },
}

SKILLS = set().union(*SKILL_CATEGORIES.values())


def preprocess(text):
    """Normalize text for keyword and skill matching."""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9+# ]", " ", text)
    return text

SKILL_ALIASES = {
    "machine learning": ["ml"],
    "artificial intelligence": ["ai"],
    "javascript": ["js"],
    "typescript": ["ts"],
    "node.js": ["node", "nodejs", "node.js"],
    "rest api": [
        "api",
        "apis",
        "rest api",
        "rest apis",
        "restful api",
    ],
    "computer vision": ["cv"],
    "object oriented programming": ["oop"],
    "data structures and algorithms": ["dsa"],
    "database management system": ["dbms"],
    "data analysis": ["data analytics", "data analysis"],
    "power bi": ["powerbi"],
    "postgresql": ["postgres"],
    "mongodb": ["mongo"],
    "artificial intelligence": ["ai"],
    "natural language processing": ["nlp"],
    "retrieval augmented generation": ["rag"],
    "graphql": ["graphql api"],
    "natural language processing": ["nlp"],
}


def extract_skills(text):
    """
    Extract skills using whole-word matching and aliases.
    """

    normalized_text = preprocess(text)
    found_skills = set()

    # Match canonical skill names
    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, normalized_text):
            found_skills.add(skill)

    # Match aliases
    for canonical_skill, aliases in SKILL_ALIASES.items():

        for alias in aliases:

            pattern = r"\b" + re.escape(alias) + r"\b"

            if re.search(pattern, normalized_text):
                found_skills.add(canonical_skill)

    return found_skills


def calculate_text_similarity(resume, job):
    """Calculate TF-IDF cosine similarity between resume and job description."""
    documents = [resume, job]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    return round(similarity * 100, 2)


def calculate_skill_match(resume, job):
    """Compare extracted resume skills against extracted job skills."""
    resume_skills = extract_skills(resume)
    job_skills = extract_skills(job)

    if not job_skills:
        return 0, [], []

    matched_skills = sorted(resume_skills & job_skills)
    missing_skills = sorted(job_skills - resume_skills)
    coverage = len(matched_skills) / len(job_skills)

    # Slightly reward resumes that already have good coverage
    skill_score = round((coverage**0.6) * 100, 2)

    return skill_score, matched_skills, missing_skills


def experience_score(resume):
    """
    Estimate experience score from resume text.

    Supports:
    - 5 years
    - 5+ years
    - 6 months
    - 45 days
    - internships
    - projects
    """

    resume = resume.lower()

    # -------- Years --------
    year_match = re.search(r"(\d+)\s*\+?\s*years?", resume)
    if year_match:
        years = int(year_match.group(1))
        return min(70 + years * 6, 100)

    # -------- Months --------
    month_match = re.search(r"(\d+)\s*months?", resume)
    if month_match:
        months = int(month_match.group(1))
        years = months / 12
        return min(65 + years * 6, 80)

    # -------- Days --------
    day_match = re.search(r"(\d+)\s*days?", resume)
    if day_match:
        days = int(day_match.group(1))
        years = days / 365
        return min(60 + years * 6, 70)

    # -------- Student Experience --------
    student_keywords = [
        "intern",
        "internship",
        "project",
        "projects",
        "freelance",
        "research",
        "training",
        "hackathon",
        "certification",
    ]

    if any(keyword in resume for keyword in student_keywords):
        return 65

    # -------- No Experience --------
    return 50


def final_match_score(resume, job):
    """Calculate final ATS score and return detailed match results."""
    text_score = calculate_text_similarity(resume, job)
    skill_score, matched_skills, missing_skills = calculate_skill_match(resume, job)
    exp_score = experience_score(resume)
    final_score = round(
        (SKILL_WEIGHT * skill_score)
        + (TEXT_WEIGHT * text_score)
        + (EXPERIENCE_WEIGHT * exp_score),
        2,
    )

    suggestions = []

    if missing_skills:
        suggestions.append("Consider adding these skills: " + ", ".join(missing_skills))

    if exp_score < 60:
        suggestions.append("Highlight internships, projects or practical experience.")

    if final_score > 85:
        recommendation = "Excellent Fit"
    elif final_score > 70:
        recommendation = "Good Fit"
    elif final_score > 50:
        recommendation = "Fair Fit"
    else:
        recommendation = "Needs Improvement"

    return {
        "ats_score": final_score,
        "text_similarity": text_score,
        "skill_score": skill_score,
        "experience_score": exp_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendation": recommendation,
        "suggestions": suggestions,
    }
