import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILL_WEIGHT = 0.50
TEXT_WEIGHT = 0.30
EXPERIENCE_WEIGHT = 0.20

SKILL_DATABASE = {
    # ===========================
    # Programming Languages
    # ===========================
    "python": {
        "display": "Python",
        "category": "programming_languages",
        "aliases": ["py"],
        "group": None,
    },
    "java": {
        "display": "Java",
        "category": "programming_languages",
        "aliases": [],
        "group": None,
    },
    "c": {
        "display": "C",
        "category": "programming_languages",
        "aliases": [],
        "group": None,
    },
    "c++": {
        "display": "C++",
        "category": "programming_languages",
        "aliases": ["cpp"],
        "group": None,
    },
    "javascript": {
        "display": "JavaScript",
        "category": "programming_languages",
        "aliases": ["js"],
        "group": None,
    },
    "typescript": {
        "display": "TypeScript",
        "category": "programming_languages",
        "aliases": ["ts"],
        "group": None,
    },
    "go": {
        "display": "Go",
        "category": "programming_languages",
        "aliases": ["golang"],
        "group": None,
    },
    # ===========================
    # Frontend
    # ===========================
    "html": {
        "display": "HTML",
        "category": "frontend",
        "aliases": [],
        "group": None,
    },
    "css": {
        "display": "CSS",
        "category": "frontend",
        "aliases": [],
        "group": None,
    },
    "bootstrap": {
        "display": "Bootstrap",
        "category": "frontend",
        "aliases": [],
        "group": None,
    },
    "tailwind": {
        "display": "Tailwind CSS",
        "category": "frontend",
        "aliases": ["tailwindcss"],
        "group": None,
    },
    "react": {
        "display": "React",
        "category": "frontend",
        "aliases": ["react.js", "reactjs"],
        "group": None,
    },
    "angular": {
        "display": "Angular",
        "category": "frontend",
        "aliases": [],
        "group": None,
    },
    "vue": {
        "display": "Vue.js",
        "category": "frontend",
        "aliases": ["vuejs"],
        "group": None,
    },
    # ===========================
    # Backend
    # ===========================
    "flask": {
        "display": "Flask",
        "category": "backend",
        "aliases": [],
        "group": "python_framework",
    },
    "django": {
        "display": "Django",
        "category": "backend",
        "aliases": [],
        "group": "python_framework",
    },
    "fastapi": {
        "display": "FastAPI",
        "category": "backend",
        "aliases": [],
        "group": "python_framework",
    },
    "node.js": {
        "display": "Node.js",
        "category": "backend",
        "aliases": ["node", "nodejs"],
        "group": "backend_runtime",
    },
    "express": {
        "display": "Express.js",
        "category": "backend",
        "aliases": ["expressjs"],
        "group": "backend_framework",
    },
    "rest api": {
        "display": "REST API",
        "category": "backend",
        "aliases": [
            "api",
            "apis",
            "rest api",
            "rest apis",
            "restful api",
        ],
        "group": "api_style",
    },
    "graphql": {
        "display": "GraphQL",
        "category": "backend",
        "aliases": ["graphql api"],
        "group": "api_style",
    },
    "grpc": {
        "display": "gRPC",
        "category": "backend",
        "aliases": [],
        "group": "api_style",
    },
    # ===========================
    # Databases
    # ===========================
    "sql": {
        "display": "SQL",
        "category": "database",
        "aliases": [],
        "group": "database_type",
    },
    "mysql": {
        "display": "MySQL",
        "category": "database",
        "aliases": [],
        "group": "relational_database",
    },
    "postgresql": {
        "display": "PostgreSQL",
        "category": "database",
        "aliases": ["postgres"],
        "group": "relational_database",
    },
    "sqlite": {
        "display": "SQLite",
        "category": "database",
        "aliases": [],
        "group": "relational_database",
    },
    "mongodb": {
        "display": "MongoDB",
        "category": "database",
        "aliases": ["mongo"],
        "group": "nosql_database",
    },
    "dynamodb": {
        "display": "DynamoDB",
        "category": "database",
        "aliases": [],
        "group": "nosql_database",
    },
    "redis": {
        "display": "Redis",
        "category": "database",
        "aliases": [],
        "group": "cache_database",
    },
    "pinecone": {
        "display": "Pinecone",
        "category": "database",
        "aliases": [],
        "group": "vector_database",
    },
    "qdrant": {
        "display": "Qdrant",
        "category": "database",
        "aliases": [],
        "group": "vector_database",
    },
    "chromadb": {
        "display": "ChromaDB",
        "category": "database",
        "aliases": ["chroma"],
        "group": "vector_database",
    },
    # ===========================
    # Cloud / DevOps
    # ===========================
    "aws": {
        "display": "AWS",
        "category": "cloud_devops",
        "aliases": ["amazon web services"],
        "group": "cloud_provider",
    },
    "gcp": {
        "display": "GCP",
        "category": "cloud_devops",
        "aliases": ["google cloud", "google cloud platform"],
        "group": "cloud_provider",
    },
    "azure": {
        "display": "Microsoft Azure",
        "category": "cloud_devops",
        "aliases": ["azure cloud"],
        "group": "cloud_provider",
    },
    "docker": {
        "display": "Docker",
        "category": "cloud_devops",
        "aliases": [],
        "group": "containerization",
    },
    "kubernetes": {
        "display": "Kubernetes",
        "category": "cloud_devops",
        "aliases": ["k8s"],
        "group": "container_orchestration",
    },
    "terraform": {
        "display": "Terraform",
        "category": "cloud_devops",
        "aliases": [],
        "group": "infrastructure_as_code",
    },
    "cloudformation": {
        "display": "CloudFormation",
        "category": "cloud_devops",
        "aliases": [],
        "group": "infrastructure_as_code",
    },
    # ===========================
    # Messaging
    # ===========================
    "kafka": {
        "display": "Apache Kafka",
        "category": "messaging",
        "aliases": [],
        "group": "message_queue",
    },
    "rabbitmq": {
        "display": "RabbitMQ",
        "category": "messaging",
        "aliases": [],
        "group": "message_queue",
    },
    # ===========================
    # Authentication
    # ===========================
    "oauth2": {
        "display": "OAuth2",
        "category": "security",
        "aliases": ["oauth"],
        "group": "authentication",
    },
    "jwt": {
        "display": "JWT",
        "category": "security",
        "aliases": ["json web token"],
        "group": "authentication",
    },
    # ===========================
    # AI / ML
    # ===========================
    "machine learning": {
        "display": "Machine Learning",
        "category": "ai_ml",
        "aliases": ["ml"],
        "group": None,
    },
    "deep learning": {
        "display": "Deep Learning",
        "category": "ai_ml",
        "aliases": [],
        "group": None,
    },
    "artificial intelligence": {
        "display": "Artificial Intelligence",
        "category": "ai_ml",
        "aliases": ["ai"],
        "group": None,
    },
    "natural language processing": {
        "display": "Natural Language Processing",
        "category": "ai_ml",
        "aliases": ["nlp"],
        "group": None,
    },
    "computer vision": {
        "display": "Computer Vision",
        "category": "ai_ml",
        "aliases": ["cv"],
        "group": None,
    },
    "rag": {
        "display": "Retrieval-Augmented Generation",
        "category": "ai_ml",
        "aliases": ["retrieval augmented generation"],
        "group": None,
    },
}

def preprocess(text):
    """Normalize text for keyword and skill matching."""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9+# ]", " ", text)
    return text


REQUIRED_HEADERS = [
    "required skills",
    "required qualifications",
    "minimum qualifications",
    "requirements",
    "qualifications",
    "must have",
]

OPTIONAL_HEADERS = [
    "preferred",
    "preferred qualifications",
    "nice to have",
    "bonus",
    "good to have",
]


def extract_skills(text):
    """
    Extract skills using the unified SKILL_DATABASE.
    """

    normalized_text = preprocess(text)
    found_skills = set()

    for canonical_skill, metadata in SKILL_DATABASE.items():

        # Match canonical skill
        pattern = r"\b" + re.escape(canonical_skill) + r"\b"

        if re.search(pattern, normalized_text):
            found_skills.add(canonical_skill)
            continue

        # Match aliases
        for alias in metadata["aliases"]:

            pattern = r"\b" + re.escape(alias) + r"\b"

            if re.search(pattern, normalized_text):
                found_skills.add(canonical_skill)
                break

    return found_skills


def parse_job_description(job_text):

    text = preprocess(job_text)

    required_text = text
    optional_text = ""

    # Find optional section
    optional_index = len(text)

    for header in OPTIONAL_HEADERS:
        index = text.find(header)
        if index != -1:
            optional_index = min(optional_index, index)

    # Find required section
    required_found = False

    for header in REQUIRED_HEADERS:
        index = text.find(header)
        if index != -1:
            required_found = True
            required_text = text[index:optional_index]
            break

    if optional_index < len(text):
        optional_text = text[optional_index:]

    # Fallback:
    if not required_found:
        required_text = text

    return {
        "required": extract_skills(required_text),
        "optional": extract_skills(optional_text),
    }


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
    job_data = parse_job_description(job)

    required_skills = job_data["required"]
    optional_skills = job_data["optional"]

    job_skills = required_skills | optional_skills

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
