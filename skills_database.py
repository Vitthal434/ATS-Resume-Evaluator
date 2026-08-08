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
        "group": "None",
    },
    "django": {
        "display": "Django",
        "category": "backend",
        "aliases": [],
        "group": "None",
    },
    "fastapi": {
        "display": "FastAPI",
        "category": "backend",
        "aliases": [],
        "group": "None",
    },
    "node.js": {
        "display": "Node.js",
        "category": "backend",
        "aliases": ["node", "nodejs"],
        "group": "None",
    },
    "express": {
        "display": "Express.js",
        "category": "backend",
        "aliases": ["expressjs"],
        "group": "None",
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
        "group": "None",
    },
    "graphql": {
        "display": "GraphQL",
        "category": "backend",
        "aliases": ["graphql api"],
        "group": "None",
    },
    "grpc": {
        "display": "gRPC",
        "category": "backend",
        "aliases": [],
        "group": "None",
    },
    # ===========================
    # Databases
    # ===========================
    "sql": {
        "display": "SQL",
        "category": "database",
        "aliases": [],
        "group": "None",
    },
    "mysql": {
        "display": "MySQL",
        "category": "database",
        "aliases": [],
        "group": "None",
    },
    "postgresql": {
        "display": "PostgreSQL",
        "category": "database",
        "aliases": ["postgres"],
        "group": "None",
    },
    "sqlite": {
        "display": "SQLite",
        "category": "database",
        "aliases": [],
        "group": "None",
    },
    "mongodb": {
        "display": "MongoDB",
        "category": "database",
        "aliases": ["mongo"],
        "group": "None",
    },
    "dynamodb": {
        "display": "DynamoDB",
        "category": "database",
        "aliases": [],
        "group": "None",
    },
    "redis": {
        "display": "Redis",
        "category": "database",
        "aliases": [],
        "group": "None",
    },
    "pinecone": {
        "display": "Pinecone",
        "category": "database",
        "aliases": [],
        "group": "None",
    },
    "qdrant": {
        "display": "Qdrant",
        "category": "database",
        "aliases": [],
        "group": "None",
    },
    "chromadb": {
        "display": "ChromaDB",
        "category": "database",
        "aliases": ["chroma"],
        "group": "None",
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
        "group": "None",
    },
    "jwt": {
        "display": "JWT",
        "category": "security",
        "aliases": ["json web token"],
        "group": "None",
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
