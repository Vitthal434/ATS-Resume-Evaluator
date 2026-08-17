# ResumeIQ — ATS Resume Evaluator

ResumeIQ is an intelligent Applicant Tracking System (ATS) resume matching and evaluation platform. It scores resumes against job descriptions, identifies skill gaps, calculates semantic and lexical text similarity, extracts experience and education, and provides downloadable PDF reports and tailored job recommendations.

---

## Features

- **ATS Compatibility Scoring:** Multi-component weighted scoring algorithm (50% Skill Match, 30% Text Similarity, 20% Experience Match).
- **Hybrid Similarity Engine:** Combines TF-IDF lexical vector matching (30%) with `SentenceTransformer` (`all-MiniLM-L6-v2`) semantic embeddings (70%).
- **Skill Extraction & Canonicalization:** Domain-based skill database covering 14+ technical domains, canonical name resolution, alias index mapping, and OR-condition alternative grouping.
- **Fast Startup & Pre-Warming:** Background thread pre-warming loads SentenceTransformer weights on app launch, reducing first user submission latency to ~150ms.
- **Interactive Web Dashboard & Reports:** Clean Bootstrap 5 web interface (`/`, `/analyze`, `/match`) with real-time loading feedback and downloadable PDF reports rendered via ReportLab.
- **Comprehensive Test Suite:** 52 unit, integration, and synthetic dataset benchmark tests ensuring 100% regression safety.
- **Containerized Deployment:** Production-grade `Dockerfile`, `docker-compose.yml`, and `render.yaml` configured with non-root execution and Waitress WSGI serving.

---

## Environment Variables

| Variable | Description | Default (Dev) | Production |
|----------|-------------|---------------|------------|
| `SECRET_KEY` | Flask session and CSRF security key | `resumeiq-default-dev-key` | Render Auto-Generated Secret |
| `PORT` | Web server listening port | `5000` | Set dynamically by cloud host |
| `WERKZEUG_RUN_MAIN` | Flask debug reloader process indicator | Auto-set by Flask | Unset in production |

> **Production Note:** Set a strong random secret key in production environments:
> ```bash
> export SECRET_KEY="your-production-secure-random-key"
> ```

---

## Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd "ATS Resume Evaluator"
   ```

2. **Set Up Virtual Environment:**
   ```bash
   python -m venv resumeiq-venv
   .\resumeiq-venv\Scripts\activate   # On Windows
   # source resumeiq-venv/bin/activate  # On Linux/macOS
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Application

### Development Server
Runs the Flask application with debug reloader enabled:
```bash
python app.py
```
Access the application at `http://127.0.0.1:5000`.

### Production Server (WSGI)
For Windows and production environments using **Waitress**:
```bash
python wsgi.py
```
*Or using the command line:*
```bash
waitress-serve --host=0.0.0.0 --port=5000 wsgi:application
```

### Health Check Endpoint
- **GET `/health`**: Returns `{"status": "ok"}` (lightweight JSON check for load balancers and deployment monitoring, avoiding SentenceTransformer invocation).

---

## Docker Deployment

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### 1. Build Docker Image
```bash
docker build -t resumeiq .
```

### 2. Run Container with Docker Compose
```bash
docker compose up -d
```
Access the containerized application at `http://localhost:5000`.

### 3. Container Management Commands
- **View Container Logs:**
  ```bash
  docker compose logs -f
  ```
- **Stop Container:**
  ```bash
  docker compose down
  ```
- **Rebuild Image After Code Changes:**
  ```bash
  docker compose up -d --build
  ```

---

## Cloud Deployment (Render)

ResumeIQ is configured for automated container deployment on **Render** using the repository's [`Dockerfile`](file:///c:/Users/DELL/Documents/ATS%20Resume%20Evaluator/ATS-Resume-Evaluator/Dockerfile) and [`render.yaml`](file:///c:/Users/DELL/Documents/ATS%20Resume%20Evaluator/ATS-Resume-Evaluator/render.yaml).

### Platform Selection Rationale
- **Render** was chosen because it natively supports Docker deployment from GitHub, provides an automated HTTP health check probe (`/health`), manages SSL certificates out of the box, and runs the application via Waitress WSGI without complex cloud infrastructure.

### Production Live URL (Placeholder)
- `https://resumeiq.onrender.com`

### Deployment Steps (Step-by-Step)

#### Method A: Render Blueprint (Recommended)
1. Push your code to your GitHub repository.
2. Log in to [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** -> **Blueprint**.
4. Connect your GitHub repository containing `render.yaml`.
5. Render will automatically detect `render.yaml`, set up the Docker Web Service, configure `SECRET_KEY`, and deploy.

#### Method B: Manual Web Service Setup
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Select **Docker** as the Environment.
5. Set Health Check Path to `/health`.
6. Add Environment Variable: `SECRET_KEY` = `<your-secure-random-secret>`.
7. Click **Create Web Service**.

### Cloud Troubleshooting Notes
- **Cold Start Delay:** Free-tier container instances may spin down after inactivity. Initial request after spin-down may take ~15-30s while the container boots and SentenceTransformer weights load in memory.
- **Memory Requirements:** Ensure container allocation is at least 512 MB RAM to accommodate PyTorch and SentenceTransformer embeddings.

---

## Advanced AI Enhancements (Stage 9)

ResumeIQ includes optional LLM-driven AI capabilities using Gemini 1.5 Flash:

1. **AI Resume Bullet Optimization (Stage 9.1):** Endpoint `POST /api/ai/improve` parses resume experience statements against JD requirements and suggests non-hallucinated bullet revisions.
2. **AI Complex JD Semantic Parsing (Stage 9.2):** Endpoint `POST /api/ai/parse-jd` converts raw, ambiguous job descriptions into structured JSON schemas (required/preferred skills, alternative OR groups, experience requirements, education, and responsibilities).

> **Architectural Guarantee:** LLM semantic parsing and bullet optimization are purely optional downstream enhancements. The core deterministic ATS scoring engine (50% Skill, 30% Text Similarity, 20% Experience) remains 100% authoritative and works completely offline without `GEMINI_API_KEY`.

### Environment Configuration for AI Features
```bash
# Optional: Enable Gemini LLM features
export GEMINI_API_KEY="your-gemini-api-key"
```

---

## Running Tests

Execute the complete 65-test verification suite:

```bash
# 1. Core Matching Engine Unit Tests (13 tests)
python tests/test_matcher_unit.py

# 2. ATS Scoring Validation Suite (16 tests)
python tests/test_scoring_validation.py

# 3. Text Similarity Evaluation Suite (13 tests)
python tests/test_text_similarity_eval.py

# 4. Flask API Route Integration Tests (8 tests including GET /health)
python tests/test_api_routes.py

# 5. Synthetic Evaluation Dataset Benchmark (2 tests / 15 dataset cases)
python tests/test_evaluation_benchmark.py

# 6. AI Resume Improver Unit Tests (5 tests)
python tests/test_ai_improver.py

# 7. AI Semantic JD Parser Unit Tests (8 tests)
python tests/test_jd_semantic_parser.py
```

---

## Project Structure

```text
ATS Resume Evaluator/
├── Dockerfile                  # Production container definition (Python 3.12-slim + Waitress)
├── docker-compose.yml          # Local container orchestration file
├── .dockerignore               # Docker build context exclusion rules
├── render.yaml                 # Render Cloud Deployment Blueprint specification
├── .github/workflows/ci.yml    # GitHub Actions automated CI/CD pipeline
├── app.py                      # Flask web app & routes (/health, /match, /api/ai/improve, /api/ai/parse-jd)
├── wsgi.py                     # Production WSGI server entrypoint (Waitress + PORT env support)
├── matcher.py                  # ATS scoring algorithm & hybrid similarity engine
├── text_similarity.py          # TF-IDF text similarity module
├── job_recommender.py          # Canonical skill job recommendation engine
├── report_generator.py        # ReportLab PDF report generator & skill formatter
├── resume_parser.py           # PyPDF2 and python-docx text extraction
├── ai/                         # Optional LLM AI Enhancement Layer
│   ├── __init__.py
│   ├── gemini_provider.py      # Gemini REST API authentication & provider service
│   ├── resume_improver.py      # Non-hallucination bullet optimization engine
│   └── jd_semantic_parser.py   # Complex JD semantic schema parser
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore specifications
├── skills/                     # Domain skill databases & alias resolution
├── templates/                  # Jinja2 HTML templates (landing, analyze, dashboard, base)
├── static/                     # CSS stylesheets & JavaScript files
├── docs/                       # Project specifications and progress tracking
│   ├── PROJECT_SPEC.md
│   └── PROJECT_PROGRESS.md
└── tests/                      # Verification and benchmarking test suites
    ├── evaluation_dataset.json
    ├── test_ai_improver.py      # 5 unit tests for AI bullet optimization
    ├── test_api_routes.py      # 8 integration tests including GET /health
    ├── test_evaluation_benchmark.py # Benchmark suite for 15 domain cases
    ├── test_jd_semantic_parser.py # 8 unit tests for AI JD semantic parsing
    ├── test_matcher_unit.py    # 13 unit tests for matcher module
    ├── test_scoring_validation.py # 16 unit tests for ATS scoring algorithm
    └── test_text_similarity_eval.py # 13 unit tests for similarity engine
```