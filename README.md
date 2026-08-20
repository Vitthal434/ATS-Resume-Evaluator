# ResumeIQ — ATS Resume Evaluator

ResumeIQ is an intelligent Applicant Tracking System (ATS) resume matching and evaluation platform. It scores resumes against job descriptions, identifies skill gaps, calculates semantic and lexical text similarity, extracts experience and education, provides downloadable PDF reports, and recommends relevant career paths.

---

## 🚀 Live Demo

- **Public Demo:** [Try ResumeIQ on Render](https://resumeiq-6baf.onrender.com)
- **GitHub Repository:** [Vitthal434/ATS-Resume-Evaluator](https://github.com/Vitthal434/ATS-Resume-Evaluator)

> **Note:** This deployment is a free public portfolio / college-project demonstration hosted on Render's free tier. All deterministic ATS scoring, skill matching, gap analysis, career recommendations, and PDF generation features are fully functional online.

---

## Features

- **ATS Compatibility Scoring:** Multi-component weighted scoring algorithm (50% Skill Match, 30% Text Similarity, 20% Experience Match).
- **Hybrid Similarity Engine:** Combines TF-IDF lexical vector matching (30%) with `SentenceTransformer` (`all-MiniLM-L6-v2`) semantic embeddings (70%).
- **Skill Extraction & Canonicalization:** Domain-based skill database covering 14+ technical domains, canonical name resolution, alias index mapping, and OR-condition alternative grouping.
- **Partial & Transferable Skill Matching:** Conservative 50% partial credit for related/transferable technologies within the same domain.
- **Experience & Education Analysis:** Heuristic extraction of candidate years of experience, degree level, and requirement alignment.
- **Intelligent Gap Analysis:** Structured breakdown of missing, partial, and exact skills categorized by requirement urgency (CRITICAL, HIGH, MEDIUM, LOW).
- **Prioritized Improvement Roadmap:** Deterministic 3-tier action plan (Immediate, Next, Optional) to guide resume optimization.
- **Skill-Based Career Recommendations:** Deterministic matching against predefined career role profiles based on extracted candidate skills.
- **Interactive Web Dashboard & Reports:** Clean Bootstrap 5 web interface (`/`, `/analyze`, `/match`) with real-time feedback and downloadable PDF reports rendered via ReportLab.
- **Optional AI Resume Bullet Optimization:** AI-assisted suggestions to strengthen resume bullet points against job requirements without hallucination.
- **Optional AI Semantic JD Parsing:** AI parsing of ambiguous job descriptions into structured requirement schemas.
- **Comprehensive 163-Test Suite:** Unit, integration, and synthetic dataset benchmark tests ensuring 100% regression safety across 13 test modules.
- **Containerized Deployment:** Production-grade `Dockerfile`, `docker-compose.yml`, and `render.yaml` configured with non-root execution and Waitress WSGI serving.

---

## Application Architecture & Workflow

ResumeIQ is built on a hybrid architecture that pairs a deterministic ATS evaluation engine with an optional local or cloud-based AI enhancement layer:

```text
Candidate Resume (PDF/DOCX)
          +
Job Description
          ↓
Presentation Layer
Bootstrap 5.3 + Vanilla JavaScript + Jinja2
          ↓
Flask Web Application / Waitress
          ↓
Document & Text Processing
PyPDF2 / python-docx
          ↓
Skill Extraction & Canonicalization
14-Domain Skill Taxonomy
          ↓
Deterministic ATS Scoring Core
          ├── 50% Skill Match
          ├── 30% Hybrid Text Similarity
          └── 20% Experience & Education
          ↓
     ┌────┴───────────────┐
     ↓                    ↓
Gap Analysis        Downstream Services
& Roadmap           Career Recommendations
                    ReportLab PDF Reports
                    Interactive Dashboard
     │
     └────────────┬────────────┘
                  ↓
       Optional AI Enhancement
       ├── Qwen2.5-0.5B GGUF
       │   via llama-cpp-python
       └── Google Gemini 1.5 Flash
```

### End-to-End Execution Flow

1. **Upload & Parse:** Accepts candidate resumes in PDF, DOC, or DOCX format alongside raw job description text. `resume_parser.py` uses PyPDF2 and python-docx to extract, sanitize, and normalize text streams.
2. **Skill Extraction & Normalization:** The `skills/` module scans text against a 14-domain skill taxonomy, resolves aliases and abbreviations to canonical tokens via `ALIAS_INDEX`, and groups OR-condition alternatives.
3. **ATS Scoring:** `matcher.py` computes an authoritative, weighted ATS compatibility score using the 50/30/20 formula (50% exact, partial, and OR-group skill match; 30% hybrid lexical/semantic similarity; 20% experience and education alignment).
4. **Gap Analysis & Roadmap:** `gap_analyzer.py` classifies requirements into exact matches, partial matches, and missing skills, prioritizing gaps across `CRITICAL`, `HIGH`, `MEDIUM`, and `LOW` tiers to generate a 3-tier action roadmap (`Immediate`, `Next`, `Optional`).
5. **Career Recommendations:** `job_recommender.py` evaluates extracted candidate skills against predefined career role profiles to suggest matching job paths.
6. **Report Generation:** `report_generator.py` compiles evaluation metrics into a publication-quality, downloadable multi-page PDF using ReportLab, while `app.py` renders the interactive web dashboard.
7. **Optional AI Enhancements:** The `ai/` module provides non-hallucinated resume bullet optimizations and complex JD semantic schema parsing via local GGUF (`Qwen2.5-0.5B-Instruct-GGUF` via `llama-cpp-python`) or optional Google Gemini API.

---

## Technology Stack

### Core Language & Web Application

| Category | Technology | Role in ResumeIQ |
|---|---|---|
| Programming Language | Python 3.12 | Core language for backend logic, parsers, scoring algorithms, and test suites |
| Web Framework | Flask | Request routing, session management, file upload validation, and REST API endpoints |
| WSGI Server | Waitress | Production-grade multi-threaded WSGI server for Windows and Linux container execution |
| Template Engine | Jinja2 | Server-side HTML template rendering with custom formatting filters |

### Machine Learning & NLP

| Category | Technology | Role in ResumeIQ |
|---|---|---|
| Lexical Vectorization | Scikit-learn (TF-IDF) | Sublinear TF-IDF n-gram vectorization for 30% lexical text similarity matching |
| Vector Similarity | Cosine Similarity | Mathematical cosine similarity computation between resume and JD vector spaces |
| Dense Semantic NLP | Sentence Transformers (`all-MiniLM-L6-v2`) | 384-dimensional dense neural embeddings for 70% semantic similarity matching |
| Deep Learning Runtime | PyTorch (CPU) | CPU-optimized tensor computation engine for SentenceTransformer embeddings |
| Model Weight Hub | Hugging Face Hub | Automated downloading and local caching of transformer and GGUF model weights |
| Local AI Engine | `llama-cpp-python` | High-performance C++ quantized GGUF inference engine for offline CPU execution |
| Local LLM Model | Qwen2.5-0.5B-Instruct-GGUF | Quantized (Q5_K_M) local open-source LLM for resume bullet optimization and JD parsing |
| Cloud AI Provider | Google Gemini API (1.5 Flash) | Optional cloud-based LLM provider accessed via REST API when configured |

### Document Processing & Report Generation

| Category | Technology | Role in ResumeIQ |
|---|---|---|
| PDF Extraction | PyPDF2 | Page-by-page text extraction and sanitization from candidate PDF resumes |
| DOCX Extraction | python-docx | Paragraph and structural text parsing from Microsoft Word (.docx) resumes |
| PDF Generation | ReportLab | Programmatic generation of multi-page, formatted PDF evaluation reports |

### Frontend

| Category | Technology | Role in ResumeIQ |
|---|---|---|
| Markup | HTML5 | Semantic page structure and document hierarchy |
| CSS Framework | Bootstrap 5.3 | Responsive grid layout, modals, progress bars, cards, and utility classes |
| Icon Library | Bootstrap Icons (1.11.3) | UI symbols and category indicators across landing, analyze, and dashboard views |
| Custom Styling | Vanilla CSS3 | Dark-accented design system, glassmorphism effects, and responsive styling |
| Client-Side Logic | Vanilla JavaScript (ES6+) | Drag-and-drop file upload, file validation, dynamic word counts, and UI state handling |
| Asynchronous Requests | Fetch API | Client-side asynchronous communication with AI enhancement and gap analysis endpoints |
| Template Integration | Jinja2 Templates | Modular HTML component structure (`base.html`, `landing.html`, `analyze.html`, `dashboard.html`) |

### Containerization, Deployment & CI/CD

| Category | Technology | Role in ResumeIQ |
|---|---|---|
| Containerization | Docker | Production container packaging with non-root security execution (`appuser`, UID 1000) |
| Local Orchestration | Docker Compose | Local multi-platform container orchestration and service configuration |
| Cloud Platform | Render | Free-tier Docker web service hosting with automated `/health` monitoring |
| Continuous Integration | GitHub Actions | Automated CI pipeline running the 163-test regression suite on push and PR |
| Server Interface | WSGI | Standardized Web Server Gateway Interface via `wsgi.py` |

### Testing & Quality Assurance

| Category | Technology | Role in ResumeIQ |
|---|---|---|
| Unit Testing | Python `unittest` | Native test runner executing unit and integration test suites |
| Mocking Framework | `unittest.mock` | Mocking external AI providers, network calls, and file operations |
| Integration Testing | Flask Test Client | End-to-end HTTP route and endpoint validation (including `/health` and `/match`) |
| Regression Testing | 163-Test Suite | Comprehensive automated test coverage across 13 test modules |
| Benchmark Testing | Synthetic Dataset Benchmark | Cross-domain evaluation across 15 synthetic candidate/JD test cases |

---

## ATS Scoring Methodology

ResumeIQ calculates an authoritative, deterministic ATS compatibility score using a 3-part weighted formula:

```text
ATS Score =
(0.50 × Skill Score)
+ (0.30 × Text Similarity)
+ (0.20 × Experience Score)
```

### Skill Match — 50%

The skill score evaluates candidate skills against job description requirements using a 14-domain technical taxonomy:

- **Exact & Alias Matching:** Candidate skills matching required or general JD skills receive full credit (1.0). Synonyms and abbreviations are normalized to canonical forms via `ALIAS_INDEX`:
  ```text
  js       → javascript
  postgres → postgresql
  k8s      → kubernetes
  ```
- **OR-Condition Groups:** When a job description specifies alternative requirements (e.g., `["react", "angular", "vue"]`), possessing any one of the listed skills grants full credit for that requirement group.
- **Partial Credit for Transferable Skills:** Candidate skills that are closely related within the same technical domain receive 50% partial credit (`0.5` factor) to acknowledge transferable domain competency (e.g., `fastapi` ↔ `django`).

### Hybrid Text Similarity — 30%

Text similarity measures the broader context and domain alignment between the full resume and the job description using a hybrid of lexical vectorization and dense neural embeddings:

```text
Text Similarity =
(0.30 × TF-IDF Similarity)
+ (0.70 × Semantic Similarity)
```

- **30% TF-IDF Lexical Similarity:** Evaluated using `TfidfVectorizer` with sublinear term-frequency scaling and `cosine_similarity` from `scikit-learn` to capture shared domain vocabulary and exact keyword alignment.
- **70% Semantic Similarity:** Evaluated using `SentenceTransformer("all-MiniLM-L6-v2")` to generate 384-dimensional dense semantic embeddings and calculate semantic cosine similarity, capturing conceptual relevance even when different phrasing is used.

### Experience & Education — 20%

The experience score assesses candidate seniority and academic qualification alignment:

- **Work History & Years of Experience:** Regex heuristics parse work history durations and total years of professional experience from the resume.
- **Degree Level Alignment:** Extracts academic credentials (e.g., Bachelor's, Master's, PhD) and matches them against stated JD prerequisites.
- **Requirement Comparison:** Compares candidate metrics against stated JD minimum thresholds to assign proportional experience credit.

### Fit Categorization

Based on the final composite ATS score, candidates are classified into four transparent fit tiers:

| ATS Score | Fit Category | Description |
|---|---|---|
| ≥ 85% | **Excellent Fit** | Strong alignment across required skills, semantic content, and experience requirements |
| 70%–84% | **Good Fit** | Solid qualification match with minor skill or experience gaps |
| 50%–69% | **Fair Fit** | Moderate alignment with noticeable skill gaps or partial transferable matches |
| < 50% | **Needs Improvement** | Significant gaps in core required skills or domain experience |

---

## Environment Variables

| Variable | Description | Default (Dev) | Production / Render |
|----------|-------------|---------------|---------------------|
| `SECRET_KEY` | Flask session and CSRF security key | `resumeiq-default-dev-key` | Render Auto-Generated Secret |
| `PORT` | Web server listening port | `5000` | Set dynamically by cloud host |
| `WERKZEUG_RUN_MAIN` | Flask debug reloader process indicator | Auto-set by Flask | Unset in production |
| `AI_PROVIDER` | Active AI provider (`local`, `gemini`, or `none`) | `local` | `none` (on free demo) |
| `ENABLE_MODEL_WARMUP` | Pre-warm SentenceTransformer on launch | `true` | Auto-skipped if `AI_PROVIDER=none` |

> **Production Note:** Set a strong random secret key in production environments:
> ```bash
> export SECRET_KEY="your-production-secure-random-key"
> ```

---

## Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Vitthal434/ATS-Resume-Evaluator.git
   cd ATS-Resume-Evaluator
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
- **GET `/health`**: Returns `{"status": "ok"}` (lightweight JSON check for load balancers and deployment monitoring, avoiding ML model invocation).

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

ResumeIQ is configured for automated container deployment on **Render** using the repository's [`Dockerfile`](./Dockerfile) and [`render.yaml`](./render.yaml).

### Platform Selection & Configuration
- **Platform:** Render Free (Docker Web Service).
- **Public Live Demo:** [https://resumeiq-6baf.onrender.com](https://resumeiq-6baf.onrender.com)
- **WSGI Engine:** Waitress serving port `5000` with non-root security.
- **Health Check Probe:** Automated HTTP `/health` probe.

### Deployment Dependency Strategy
The repository maintains two distinct dependency specifications:
- [`requirements.txt`](./requirements.txt): Complete environment for local development including local open-source AI support (`llama-cpp-python`, `torch`, `transformers`).
- [`requirements-render.txt`](./requirements-render.txt): Streamlined container dependencies paired with CPU-only PyTorch wheels for the lightweight free cloud deployment.

### Free-Tier Operational Notes
- **Cold Start Behavior:** Free instances on Render spin down after 15 minutes of inactivity. When a request arrives after a spin-down, the service may take a short period to wake up and start serving requests.
- **Memory Management:** To ensure reliable operation within the 512 MB memory limit, the public demo uses CPU-only wheels and loads models on demand during analysis rather than eagerly pre-warming during boot.

---

## AI Enhancements & Provider Architecture

ResumeIQ includes a modular AI provider abstraction layer supporting self-hosted open-source models and optional cloud API providers:

1. **AI Resume Bullet Optimization:** Endpoint `POST /api/ai/improve` parses resume experience statements against JD requirements and suggests non-hallucinated bullet revisions.
2. **AI Complex JD Semantic Parsing:** Endpoint `POST /api/ai/parse-jd` converts raw, ambiguous job descriptions into structured JSON schemas (required/preferred skills, alternative OR groups, experience requirements, education, and responsibilities).

> **Architectural Guarantee:** AI capabilities are strictly optional explanation and parsing enhancements. The core deterministic ATS scoring engine (50% Skill Match, 30% Text Similarity, 20% Experience Match) remains 100% authoritative and works completely offline without any AI model or API key.

### Local Development vs. Hosted Demo Configuration

- **Local Self-Hosted Usage (`AI_PROVIDER=local`):** Uses an open-source `Qwen2.5-0.5B-Instruct-GGUF` model via `llama-cpp-python` for fast, private, CPU-friendly inference with zero API fees.
- **Optional API Usage (`AI_PROVIDER=gemini`):** Connects to Google Gemini 1.5 Flash via REST API when `GEMINI_API_KEY` is provided.
- **Public Render Demo (`AI_PROVIDER=none`):** ResumeIQ uses an open-source local AI provider for self-hosted/local usage. The free Render demo runs with `AI_PROVIDER=none` to keep the public demo compatible with the platform's resource limits. All deterministic ATS features remain fully available online.

### AI Configuration & Environment Variables

| Provider | `AI_PROVIDER` | Engine / Model | Requirements |
|---|---|---|---|
| **Local Open-Source (Default)** | `local` | `Qwen/Qwen2.5-0.5B-Instruct-GGUF` (`qwen2.5-0.5b-instruct-q5_k_m.gguf`) | `llama-cpp-python` (CPU-safe, free, offline) |
| **Local Qwen3 Override** | `local` | `Qwen/Qwen3-0.6B-GGUF` (`Qwen3-0.6B-Q8_0.gguf`) | Set `GGUF_REPO_ID` and `GGUF_FILENAME` |
| **Direct Local GGUF Path** | `local` | Local `.gguf` file | Set `GGUF_MODEL_PATH="/path/to/model.gguf"` |
| **Transformers Fallback** | `local` | `Qwen/Qwen3-0.6B` | Set `LOCAL_BACKEND=transformers` |
| **Gemini API (Optional)** | `gemini` | `gemini-1.5-flash` | `GEMINI_API_KEY` environment variable |
| **Public Demo / Offline Mode** | `none` | None | Deterministic ATS core only |

```bash
# Default: Local AI provider via llama.cpp (downloads GGUF automatically on first call)
export AI_PROVIDER="local"
export LOCAL_BACKEND="auto"
export AI_BULLET_MAX_TOKENS="256"
export AI_JD_MAX_TOKENS="384"
export AI_TEMPERATURE="0.1"

# Optional: Switch to Gemini API
export AI_PROVIDER="gemini"
export GEMINI_API_KEY="your-gemini-api-key"

# Public Demo / Disabled AI Mode
export AI_PROVIDER="none"
```

---

## Running Tests

Execute the complete 163-test verification suite:

```bash
# 1. AI Provider Abstraction Unit Tests (38 tests)
python tests/test_ai_provider.py

# 2. AI Resume Improver Unit Tests (8 tests)
python tests/test_ai_improver.py

# 3. AI Semantic JD Parser Unit Tests (8 tests)
python tests/test_jd_semantic_parser.py

# 4. Gap Analysis Unit Tests (15 tests)
python tests/test_gap_analysis.py

# 5. Gap Prioritization & Roadmap Unit Tests (13 tests)
python tests/test_gap_prioritization.py

# 6. Partial Credit Skill Matching Unit Tests (11 tests)
python tests/test_partial_skill_matching.py

# 7. Core Matching Engine Unit Tests (13 tests)
python tests/test_matcher_unit.py

# 8. Job Recommender Unit Tests (8 tests)
python tests/test_job_recommender.py

# 9. PDF Report Generator Unit Tests (10 tests)
python tests/test_report_generator.py

# 10. ATS Scoring Validation Suite (16 tests)
python tests/test_scoring_validation.py

# 11. Text Similarity Evaluation Suite (13 tests)
python tests/test_text_similarity_eval.py

# 12. Flask API Route Integration Tests (8 tests including GET /health)
python tests/test_api_routes.py

# 13. Synthetic Evaluation Dataset Benchmark (2 tests / 15 dataset cases)
python tests/test_evaluation_benchmark.py
```

---

## Project Structure

```text
ATS Resume Evaluator/
├── Dockerfile                  # Production container definition (Python 3.12-slim + CPU PyTorch + Waitress)
├── docker-compose.yml          # Local container orchestration file
├── .dockerignore               # Docker build context exclusion rules
├── render.yaml                 # Render Cloud Deployment Blueprint specification
├── .github/workflows/ci.yml    # GitHub Actions automated CI/CD pipeline
├── app.py                      # Flask web app & routes (/health, /match, /api/ai/*, /api/gap-analysis)
├── wsgi.py                     # Production WSGI server entrypoint (Waitress + PORT env support)
├── matcher.py                  # ATS scoring algorithm & hybrid similarity engine
├── gap_analyzer.py             # Deterministic gap prioritization & roadmap engine
├── text_similarity.py          # TF-IDF text similarity module (baseline reference)
├── job_recommender.py          # Skill-based job recommendation engine
├── report_generator.py        # ReportLab PDF report generator & skill formatter
├── resume_parser.py           # PyPDF2 and python-docx text extraction
├── ai/                         # AI Provider Layer & Enhancement Modules
│   ├── __init__.py
│   ├── provider.py             # Unified AI provider abstraction & routing
│   ├── local_provider.py       # Local open-source GGUF inference engine (Qwen2.5-0.5B via llama.cpp)
│   ├── gemini_provider.py      # Optional Gemini REST API provider
│   ├── resume_improver.py      # Non-hallucination bullet optimization engine
│   └── jd_semantic_parser.py   # Complex JD semantic schema parser
├── requirements.txt            # Complete local Python dependencies (with llama-cpp-python)
├── requirements-render.txt     # Lightweight Render deployment dependencies
├── .gitignore                  # Git ignore specifications
├── skills/                     # Domain skill databases & alias resolution
├── templates/                  # Jinja2 HTML templates (landing, analyze, dashboard, base)
├── static/                     # CSS stylesheets & JavaScript files
├── docs/                       # Project specifications and progress tracking
│   ├── PROJECT_SPEC.md
│   └── PROJECT_PROGRESS.md
└── tests/                      # Verification and benchmarking test suites (163 tests)
    ├── evaluation_dataset.json
    ├── test_ai_provider.py      # 38 unit tests for provider abstraction & routing
    ├── test_ai_improver.py      # 8 unit tests for AI bullet optimization
    ├── test_jd_semantic_parser.py # 8 unit tests for AI JD semantic parsing
    ├── test_gap_analysis.py    # 15 unit tests for gap analysis engine
    ├── test_gap_prioritization.py # 13 unit tests for gap prioritization & roadmap
    ├── test_partial_skill_matching.py # 11 unit tests for partial credit matching
    ├── test_matcher_unit.py    # 13 unit tests for matcher module
    ├── test_job_recommender.py # 8 unit tests for job recommendation engine
    ├── test_report_generator.py # 10 unit tests for ReportLab PDF generator
    ├── test_scoring_validation.py # 16 unit tests for ATS scoring algorithm
    ├── test_text_similarity_eval.py # 13 unit tests for similarity engine
    ├── test_api_routes.py      # 8 integration tests including GET /health
    └── test_evaluation_benchmark.py # Benchmark suite for 15 domain cases
```
