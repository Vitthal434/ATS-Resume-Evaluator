AI_ML_SKILLS = {
    # ===========================
    # Core AI / ML
    # ===========================
    "artificial intelligence": {
        "display": "Artificial Intelligence",
        "category": "ai_ml",
        "aliases": ["ai"],
        "priority": "high",
        "related": ["machine learning", "deep learning"],
    },
    "machine learning": {
        "display": "Machine Learning",
        "category": "ai_ml",
        "aliases": ["ml"],
        "priority": "high",
        "related": ["scikit-learn", "xgboost", "lightgbm"],
    },
    "deep learning": {
        "display": "Deep Learning",
        "category": "ai_ml",
        "aliases": [],
        "priority": "high",
        "related": ["pytorch", "tensorflow", "keras"],
    },
    "natural language processing": {
        "display": "Natural Language Processing",
        "category": "ai_ml",
        "aliases": ["nlp"],
        "priority": "high",
        "related": ["transformers", "bert", "ner", "tokenization"],
    },
    "computer vision": {
        "display": "Computer Vision",
        "category": "ai_ml",
        "aliases": ["cv"],
        "priority": "high",
        "related": ["opencv", "yolo"],
    },
    # ===========================
    # ML Frameworks
    # ===========================
    "tensorflow": {
        "display": "TensorFlow",
        "category": "ai_ml",
        "aliases": ["tf"],
        "priority": "high",
        "related": ["keras", "deep learning"],
    },
    "pytorch": {
        "display": "PyTorch",
        "category": "ai_ml",
        "aliases": ["torch"],
        "priority": "high",
        "related": ["deep learning", "transformers"],
    },
    "keras": {
        "display": "Keras",
        "category": "ai_ml",
        "aliases": [],
        "priority": "medium",
        "related": ["tensorflow"],
    },
    "scikit-learn": {
        "display": "Scikit-learn",
        "category": "ai_ml",
        "aliases": ["sklearn", "scikit learn"],
        "priority": "high",
        "related": ["machine learning", "python"],
    },
    "xgboost": {
        "display": "XGBoost",
        "category": "ai_ml",
        "aliases": [],
        "priority": "high",
        "related": ["machine learning"],
    },
    "lightgbm": {
        "display": "LightGBM",
        "category": "ai_ml",
        "aliases": [],
        "priority": "medium",
        "related": ["machine learning"],
    },
    "catboost": {
        "display": "CatBoost",
        "category": "ai_ml",
        "aliases": [],
        "priority": "medium",
        "related": ["machine learning"],
    },
    # ===========================
    # NLP / Transformers
    # ===========================
    "hugging face": {
        "display": "Hugging Face",
        "category": "ai_ml",
        "aliases": ["huggingface"],
        "priority": "high",
        "related": ["transformers", "bert"],
    },
    "transformers": {
        "display": "Transformers",
        "category": "ai_ml",
        "aliases": ["hugging face transformers"],
        "priority": "high",
        "related": ["bert", "roberta", "llama", "mistral"],
    },
    "bert": {
        "display": "BERT",
        "category": "ai_ml",
        "aliases": [],
        "priority": "high",
        "related": ["transformers", "nlp", "ner"],
    },
    "roberta": {
        "display": "RoBERTa",
        "category": "ai_ml",
        "aliases": [],
        "priority": "high",
        "related": ["bert", "transformers"],
    },
    "llama": {
        "display": "LLaMA",
        "category": "ai_ml",
        "aliases": [
            "llama 2",
            "llama2",
            "llama 3",
            "llama3",
        ],
        "priority": "high",
        "related": ["llm", "transformers"],
    },
    "mistral": {
        "display": "Mistral",
        "category": "ai_ml",
        "aliases": ["mistral ai"],
        "priority": "high",
        "related": ["llm", "transformers"],
    },
    "gemma": {
        "display": "Gemma",
        "category": "ai_ml",
        "aliases": [],
        "priority": "high",
        "related": ["llm"],
    },
    "qwen": {
        "display": "Qwen",
        "category": "ai_ml",
        "aliases": ["qwen ai"],
        "priority": "high",
        "related": ["llm"],
    },
    "llm": {
        "display": "Large Language Models",
        "category": "ai_ml",
        "aliases": [
            "large language model",
            "large language models",
        ],
        "priority": "high",
        "related": ["llama", "mistral", "gemma", "qwen"],
    },
    # ===========================
    # Generative AI / RAG
    # ===========================
    "rag": {
        "display": "Retrieval-Augmented Generation",
        "category": "ai_ml",
        "aliases": [
            "retrieval augmented generation",
            "retrieval-augmented generation",
        ],
        "priority": "high",
        "related": [
            "vector database",
            "embeddings",
            "llamaindex",
            "langchain",
        ],
    },
    "embeddings": {
        "display": "Embeddings",
        "category": "ai_ml",
        "aliases": [
            "embedding",
            "text embeddings",
            "vector embeddings",
        ],
        "priority": "high",
        "related": ["rag", "vector database"],
    },
    "fine tuning": {
        "display": "Fine-tuning",
        "category": "ai_ml",
        "aliases": [
            "fine-tuning",
            "finetuning",
            "model fine tuning",
        ],
        "priority": "high",
        "related": ["transformers", "lora", "qlora"],
    },
    "lora": {
        "display": "LoRA",
        "category": "ai_ml",
        "aliases": [
            "low rank adaptation",
        ],
        "priority": "high",
        "related": ["fine tuning", "qlora"],
    },
    "qlora": {
        "display": "QLoRA",
        "category": "ai_ml",
        "aliases": [],
        "priority": "high",
        "related": ["lora", "quantization"],
    },
    "quantization": {
        "display": "Quantization",
        "category": "ai_ml",
        "aliases": [
            "model quantization",
        ],
        "priority": "high",
        "related": ["llm", "qlora"],
    },
    # ===========================
    # NLP Tasks
    # ===========================
    "ner": {
        "display": "Named Entity Recognition",
        "category": "nlp",
        "aliases": [
            "named entity recognition",
        ],
        "priority": "high",
        "related": ["nlp", "bert"],
    },
    "text classification": {
        "display": "Text Classification",
        "category": "nlp",
        "aliases": [
            "text classification",
            "document classification",
        ],
        "priority": "high",
        "related": ["nlp", "bert"],
    },
    "sentiment analysis": {
        "display": "Sentiment Analysis",
        "category": "nlp",
        "aliases": [],
        "priority": "medium",
        "related": ["nlp", "text classification"],
    },
    "text summarization": {
        "display": "Text Summarization",
        "category": "nlp",
        "aliases": [
            "summarization",
            "document summarization",
        ],
        "priority": "high",
        "related": ["nlp", "llm"],
    },
    "tokenization": {
        "display": "Tokenization",
        "category": "nlp",
        "aliases": [
            "tokenizer",
            "tokenizers",
        ],
        "priority": "high",
        "related": ["nlp", "transformers"],
    },
    # ===========================
    # GenAI Frameworks
    # ===========================
    "langchain": {
        "display": "LangChain",
        "category": "ai_ml",
        "aliases": [],
        "priority": "high",
        "related": ["rag", "llm"],
    },
    "langgraph": {
        "display": "LangGraph",
        "category": "ai_ml",
        "aliases": [],
        "priority": "high",
        "related": ["langchain", "agents"],
    },
    "llamaindex": {
        "display": "LlamaIndex",
        "category": "ai_ml",
        "aliases": [
            "llama index",
        ],
        "priority": "high",
        "related": ["rag", "llm"],
    },
    "ollama": {
        "display": "Ollama",
        "category": "ai_ml",
        "aliases": [],
        "priority": "high",
        "related": ["llm", "local llm"],
    },
    "vllm": {
        "display": "vLLM",
        "category": "ai_ml",
        "aliases": [],
        "priority": "high",
        "related": ["llm", "inference"],
    },
    # ===========================
    # Computer Vision
    # ===========================
    "opencv": {
        "display": "OpenCV",
        "category": "ai_ml",
        "aliases": ["cv2"],
        "priority": "high",
        "related": ["computer vision"],
    },
    "yolo": {
        "display": "YOLO",
        "category": "ai_ml",
        "aliases": [
            "yolo v5",
            "yolo v8",
            "yolov5",
            "yolov8",
        ],
        "priority": "high",
        "related": ["computer vision", "object detection"],
    },
    "object detection": {
        "display": "Object Detection",
        "category": "ai_ml",
        "aliases": [],
        "priority": "high",
        "related": ["computer vision", "yolo"],
    },
    # ===========================
    # Speech / Audio
    # ===========================
    "whisper": {
        "display": "Whisper",
        "category": "ai_ml",
        "aliases": ["openai whisper"],
        "priority": "high",
        "related": ["speech recognition", "nlp"],
    },
    "speech recognition": {
        "display": "Speech Recognition",
        "category": "ai_ml",
        "aliases": [
            "automatic speech recognition",
            "asr",
            "speech-to-text",
            "speech to text",
        ],
        "priority": "high",
        "related": ["whisper"],
    },
    # ===========================
    # AI APIs
    # ===========================
    "openai": {
        "display": "OpenAI",
        "category": "ai_ml",
        "aliases": [],
        "priority": "high",
        "related": ["gpt", "llm"],
    },
    "gpt": {
        "display": "GPT",
        "category": "ai_ml",
        "aliases": [
            "gpt-3",
            "gpt-4",
            "gpt-4o",
            "gpt-5",
        ],
        "priority": "high",
        "related": ["openai", "llm"],
    },
    # ===========================
    # AI Infrastructure
    # ===========================
    "cuda": {
        "display": "CUDA",
        "category": "ai_ml",
        "aliases": ["nvidia cuda"],
        "priority": "high",
        "related": ["pytorch", "gpu computing"],
    },
    "gpu computing": {
        "display": "GPU Computing",
        "category": "ai_ml",
        "aliases": [
            "gpu acceleration",
            "gpu programming",
        ],
        "priority": "medium",
        "related": ["cuda"],
    },
    "model inference": {
        "display": "Model Inference",
        "category": "ai_ml",
        "aliases": [
            "inference",
            "ml inference",
        ],
        "priority": "high",
        "related": ["vllm", "triton inference server"],
    },
    "precision": {
        "display": "Precision",
        "category": "ai_ml",
        "aliases": [
            "precision score",
        ],
        "priority": "medium",
        "related": ["recall", "f1 score"],
    },
    "recall": {
        "display": "Recall",
        "category": "ai_ml",
        "aliases": [
            "recall score",
        ],
        "priority": "medium",
        "related": ["precision", "f1 score"],
    },
    "f1 score": {
        "display": "F1 Score",
        "category": "ai_ml",
        "aliases": [
            "f1-score",
            "f1 score",
            "f1",
        ],
        "priority": "medium",
        "related": ["precision", "recall"],
    },
}
