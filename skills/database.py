DATABASE_SKILLS = {
    # ===========================
    # Relational Databases
    # ===========================
    "sql": {
        "display": "SQL",
        "category": "database",
        "aliases": ["structured query language"],
        "priority": "high",
        "related": ["postgresql", "mysql", "sqlite", "sql server", "oracle"],
    },
    "mysql": {
        "display": "MySQL",
        "category": "database",
        "aliases": [],
        "priority": "high",
        "related": ["sql", "mariadb"],
    },
    "postgresql": {
        "display": "PostgreSQL",
        "category": "database",
        "aliases": ["postgres", "postgres db"],
        "priority": "high",
        "related": ["sql", "postgis"],
    },
    "sqlite": {
        "display": "SQLite",
        "category": "database",
        "aliases": [],
        "priority": "medium",
        "related": ["sql"],
    },
    "oracle": {
        "display": "Oracle Database",
        "category": "database",
        "aliases": ["oracle db"],
        "priority": "high",
        "related": ["sql"],
    },
    "sql server": {
        "display": "SQL Server",
        "category": "database",
        "aliases": ["mssql", "microsoft sql server"],
        "priority": "high",
        "related": ["sql"],
    },
    "mariadb": {
        "display": "MariaDB",
        "category": "database",
        "aliases": [],
        "priority": "medium",
        "related": ["mysql", "sql"],
    },
    # ===========================
    # NoSQL Databases
    # ===========================
    "mongodb": {
        "display": "MongoDB",
        "category": "database",
        "aliases": ["mongo"],
        "priority": "high",
        "related": ["mongoose"],
    },
    "dynamodb": {
        "display": "DynamoDB",
        "category": "database",
        "aliases": ["amazon dynamodb"],
        "priority": "high",
        "related": ["aws"],
    },
    "cassandra": {
        "display": "Apache Cassandra",
        "category": "database",
        "aliases": [],
        "priority": "medium",
        "related": ["nosql"],
    },
    "neo4j": {
        "display": "Neo4j",
        "category": "database",
        "aliases": [],
        "priority": "medium",
        "related": ["graph database"],
    },
    # ===========================
    # Cache / Search
    # ===========================
    "redis": {
        "display": "Redis",
        "category": "database",
        "aliases": [],
        "priority": "high",
        "related": ["redis streams", "caching"],
    },
    "elasticsearch": {
        "display": "Elasticsearch",
        "category": "database",
        "aliases": ["elastic search"],
        "priority": "high",
        "related": ["opensearch", "kibana"],
    },
    "opensearch": {
        "display": "OpenSearch",
        "category": "database",
        "aliases": [],
        "priority": "medium",
        "related": ["elasticsearch"],
    },
    # ===========================
    # Vector Databases
    # ===========================
    "pinecone": {
        "display": "Pinecone",
        "category": "vector_database",
        "aliases": [],
        "priority": "high",
        "related": ["rag", "vector database"],
    },
    "qdrant": {
        "display": "Qdrant",
        "category": "vector_database",
        "aliases": [],
        "priority": "high",
        "related": ["rag", "vector database"],
    },
    "chromadb": {
        "display": "ChromaDB",
        "category": "vector_database",
        "aliases": ["chroma", "chroma db"],
        "priority": "high",
        "related": ["rag", "vector database"],
    },
    "milvus": {
        "display": "Milvus",
        "category": "vector_database",
        "aliases": [],
        "priority": "high",
        "related": ["rag", "vector database"],
    },
    "weaviate": {
        "display": "Weaviate",
        "category": "vector_database",
        "aliases": [],
        "priority": "high",
        "related": ["rag", "vector database"],
    },
    "faiss": {
        "display": "FAISS",
        "category": "vector_database",
        "aliases": [
            "facebook ai similarity search",
        ],
        "priority": "high",
        "related": ["vector database", "embeddings"],
    },
    # ===========================
    # Database Concepts
    # ===========================
    "database indexing": {
        "display": "Database Indexing",
        "category": "database",
        "aliases": ["indexing", "database indexes"],
        "priority": "high",
        "related": ["sql", "query optimization"],
    },
    "query optimization": {
        "display": "Query Optimization",
        "category": "database",
        "aliases": ["query tuning", "sql query optimization"],
        "priority": "high",
        "related": ["sql", "database indexing"],
    },
    "transactions": {
        "display": "Database Transactions",
        "category": "database",
        "aliases": ["database transactions", "transaction management"],
        "priority": "medium",
        "related": ["sql", "acid"],
    },
    "acid": {
        "display": "ACID",
        "category": "database",
        "aliases": ["acid transactions"],
        "priority": "medium",
        "related": ["transactions", "sql"],
    },
    "orm": {
        "display": "ORM",
        "category": "database",
        "aliases": [
            "object relational mapping",
            "object-relational mapping",
        ],
        "priority": "medium",
        "related": ["database"],
    },
    "mongoose": {
        "display": "Mongoose",
        "category": "database",
        "aliases": [],
        "priority": "medium",
        "related": ["mongodb", "node.js"],
    },
    "postgis": {
        "display": "PostGIS",
        "category": "database",
        "aliases": [],
        "priority": "medium",
        "related": ["postgresql"],
    },
    # ===========================
    # Data Processing
    # ===========================
    "spark": {
        "display": "Apache Spark",
        "category": "data_engineering",
        "aliases": ["apache spark"],
        "priority": "high",
        "related": ["hadoop", "pyspark"],
    },
    "pyspark": {
        "display": "PySpark",
        "category": "data_engineering",
        "aliases": [],
        "priority": "high",
        "related": ["spark", "python"],
    },
    "hadoop": {
        "display": "Hadoop",
        "category": "data_engineering",
        "aliases": ["apache hadoop"],
        "priority": "medium",
        "related": ["spark", "hdfs"],
    },
    "hdfs": {
        "display": "HDFS",
        "category": "data_engineering",
        "aliases": [
            "hadoop distributed file system",
        ],
        "priority": "medium",
        "related": ["hadoop"],
    },
    "pandas": {
        "display": "Pandas",
        "category": "data_science",
        "aliases": ["pd"],
        "priority": "high",
        "related": ["numpy", "python"],
    },
    "numpy": {
        "display": "NumPy",
        "category": "data_science",
        "aliases": ["np"],
        "priority": "high",
        "related": ["pandas", "python"],
    },
    "caching": {
        "display": "Caching",
        "category": "database",
        "aliases": [
            "cache",
            "caching strategies",
            "caching strategy",
        ],
        "priority": "high",
        "related": ["redis", "database"],
    },
    "transactional integrity": {
        "display": "Transactional Integrity",
        "category": "database",
        "aliases": [
            "transaction integrity",
            "transactional consistency",
        ],
        "priority": "high",
        "related": ["transactions", "acid", "sql"],
    },
    "database schema": {
        "display": "Database Schema",
        "category": "database",
        "aliases": [
            "database schemas",
            "relational schema",
            "database design",
        ],
        "priority": "high",
        "related": ["sql", "postgresql", "mysql"],
    },
}
