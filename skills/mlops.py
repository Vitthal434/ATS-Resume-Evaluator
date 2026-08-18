MLOPS_SKILLS = {
    # ===========================
    # Experiment Tracking
    # ===========================
    "mlflow": {
        "display": "MLflow",
        "category": "mlops",
        "aliases": [],
        "priority": "high",
        "related": ["model tracking", "experiment tracking"],
    },
    "weights and biases": {
        "display": "Weights & Biases",
        "category": "mlops",
        "aliases": [
            "wandb",
            "weights & biases",
        ],
        "priority": "high",
        "related": ["mlflow", "experiment tracking"],
    },
    "neptune": {
        "display": "Neptune.ai",
        "category": "mlops",
        "aliases": ["neptune ai"],
        "priority": "medium",
        "related": ["experiment tracking"],
    },
    # ===========================
    # ML Pipelines
    # ===========================
    "kubeflow": {
        "display": "Kubeflow",
        "category": "mlops",
        "aliases": [],
        "priority": "high",
        "related": ["kubernetes", "mlflow"],
    },
    "airflow": {
        "display": "Apache Airflow",
        "category": "mlops",
        "aliases": ["apache airflow"],
        "priority": "high",
        "related": ["ml pipelines", "data engineering"],
    },
    "dvc": {
        "display": "DVC",
        "category": "mlops",
        "aliases": [
            "data version control",
        ],
        "priority": "medium",
        "related": ["git", "mlflow"],
    },
    "kfp": {
        "display": "Kubeflow Pipelines",
        "category": "mlops",
        "aliases": [
            "kubeflow pipelines",
        ],
        "priority": "medium",
        "related": ["kubeflow"],
    },
    # ===========================
    # Model Serving
    # ===========================
    "triton inference server": {
        "display": "Triton Inference Server",
        "category": "mlops",
        "aliases": [
            "triton",
            "nvidia triton",
            "nvidia triton inference server",
        ],
        "priority": "high",
        "related": ["model inference", "cuda"],
    },
    "torchserve": {
        "display": "TorchServe",
        "category": "mlops",
        "aliases": [],
        "priority": "medium",
        "related": ["pytorch", "model serving"],
    },
    "tensorflow serving": {
        "display": "TensorFlow Serving",
        "category": "mlops",
        "aliases": [
            "tf serving",
        ],
        "priority": "medium",
        "related": ["tensorflow", "model serving"],
    },
    "bentoml": {
        "display": "BentoML",
        "category": "mlops",
        "aliases": [],
        "priority": "medium",
        "related": ["model serving"],
    },
    "seldon": {
        "display": "Seldon",
        "category": "mlops",
        "aliases": [
            "seldon core",
        ],
        "priority": "medium",
        "related": ["kubernetes", "model serving"],
    },
    # ===========================
    # Feature Management
    # ===========================
    "feast": {
        "display": "Feast",
        "category": "mlops",
        "aliases": [],
        "priority": "medium",
        "related": ["feature store"],
    },
    "feature store": {
        "display": "Feature Store",
        "category": "mlops",
        "aliases": [
            "feature stores",
        ],
        "priority": "medium",
        "related": ["feast"],
    },
    # ===========================
    # Model Management
    # ===========================
    "model registry": {
        "display": "Model Registry",
        "category": "mlops",
        "aliases": [
            "model registry",
            "model registries",
        ],
        "priority": "medium",
        "related": ["mlflow"],
    },
    "model monitoring": {
        "display": "Model Monitoring",
        "category": "mlops",
        "aliases": [
            "ml model monitoring",
        ],
        "priority": "high",
        "related": ["mlflow", "model drift"],
    },
    "model drift": {
        "display": "Model Drift",
        "category": "mlops",
        "aliases": [
            "data drift",
            "concept drift",
        ],
        "priority": "medium",
        "related": ["model monitoring"],
    },
    # ===========================
    # MLOps Concepts
    # ===========================
    "mlops": {
        "display": "MLOps",
        "category": "mlops",
        "aliases": [
            "machine learning operations",
        ],
        "priority": "high",
        "related": [
            "mlflow",
            "kubeflow",
            "model monitoring",
        ],
    },
    "model deployment": {
        "display": "Model Deployment",
        "category": "mlops",
        "aliases": [
            "ml model deployment",
        ],
        "priority": "high",
        "related": ["model serving", "mlops"],
    },
    "model serving": {
        "display": "Model Serving",
        "category": "mlops",
        "aliases": [
            "ml model serving",
        ],
        "priority": "high",
        "related": ["model deployment", "triton inference server"],
    },
    "experiment tracking": {
        "display": "Experiment Tracking",
        "category": "mlops",
        "aliases": [
            "experiment management",
        ],
        "priority": "medium",
        "related": ["mlflow", "weights and biases"],
    },
}
