# ResumeIQ Project Specification

## Project Goal
ResumeIQ (ATS Resume Evaluator) is an intelligent application designed to analyze and score resumes against specific job descriptions. It provides detailed feedback, skill gap analysis, intelligent improvement roadmaps, and tailored job recommendations by simulating standard Applicant Tracking Systems (ATS) combined with advanced semantic matching and optional local/open-source AI enhancements.

## Architecture
**CURRENT**
* **Backend:** Flask application (`app.py`) handling file uploads, text parsing, REST API routes, and web views.
* **Production Serving:** WSGI entrypoint (`wsgi.py`) powered by Waitress with containerized deployment support.
* **Deterministic Core Matching Engine:** Custom scoring pipeline (`matcher.py`) implementing 50% Skill Match, 30% Hybrid Text Similarity, and 20% Experience Match.
* **Skill Engine:** Granular, domain-specific skill dictionary architecture across 14 modules in the `skills/` package with canonical mapping and alias resolution.
* **Gap Analysis & Roadmap Engine:** Deterministic skill gap prioritization, timeline estimation, and structured improvement roadmaps (`gap_analyzer.py`).
* **Job Recommendation Engine:** Domain-aware career pathway suggestions based on matched skills (`job_recommender.py`).
* **Machine Learning:** `scikit-learn` for TF-IDF lexical vectorization and `sentence-transformers` (`all-MiniLM-L6-v2`) for semantic embeddings.
* **Reporting:** Visual, multi-page branded PDF reports generated using `reportlab` (`report_generator.py`).
* **AI Provider Layer (`ai/`):** Provider abstraction layer (`ai/provider.py`) supporting local open-source CPU inference (`ai/local_provider.py` via `llama-cpp-python` and GGUF quantized models) with optional Gemini REST API fallback (`ai/gemini_provider.py`). Deterministic ATS scoring is 100% independent of the AI layer.
* **Containerization & Deployment:** Production `Dockerfile` (Python 3.12-slim, non-root user), `docker-compose.yml`, and `render.yaml` Blueprint.

## ATS Matching Pipeline
1. **Parsing:** Extracts text from uploaded PDF/DOCX resumes (`resume_parser.py`).
2. **JD Segmentation:** Splits the Job Description into sections (general, required, optional, responsibilities) based on keyword headers.
3. **Extraction:** Identifies canonical skills, alternative OR-requirements, experience durations, and education keywords.
4. **Partial Credit Matching:** Awards 50% partial credit for explicitly related/transferable skills within the same domain.
5. **Scoring:** Calculates component scores for text similarity, skill match (with weighting for required/general/optional), and experience.
6. **Aggregation:** Combines sub-scores into a final weighted ATS match score (50/30/20).
7. **Gap Analysis & Roadmap:** Analyzes missing skills, assigns urgency levels, and builds a step-by-step career improvement roadmap.
8. **Reporting:** Renders an interactive web dashboard and generates a downloadable multi-page PDF report.

## Skill Database Architecture
* **Modularization:** Factored into domain modules (e.g., `programming.py`, `cloud.py`, `frontend.py`, `ai_ml.py`) unified in `skills/__init__.py`.
* **Normalization:** Enforces canonical naming, category, and default priority for each skill.
* **Alias Handling:** Automatically builds an alias index and strips ambiguous aliases mapping to multiple canonical skills.
* **Related Skills:** Conservative, intra-domain relationships for transferable skill matching.

## JD Skill Extraction & OR-Condition Matching
* Preprocesses text while preserving domain-specific tokens (e.g., `C++`, `Node.js`, `.NET`).
* Extracts canonical skills using boundary patterns and resolves overlapping mentions by preferring longest matches.
* Detects alternative skill requirements separated by "or" or slashes (e.g., "AWS or GCP", "Python / Go") and scores them collectively.

## Semantic/Text Similarity Engine
* **Lexical:** TF-IDF vectorization with cosine similarity (30% weight).
* **Semantic:** `SentenceTransformer` (`all-MiniLM-L6-v2`) embeddings with cosine similarity (70% weight).
* **Hybrid Score:** Combines semantic and lexical scores into a unified similarity percentage.

## Experience Scoring
* Heuristic extraction of experience durations (years, months) and student/internship indicators.
* Calculates a baseline score based on the highest extracted experience time.

## Final ATS Scoring
* **Formula:** Skill Match (50%) + Text Similarity (30%) + Experience Score (20%).
* **Fit Categories:** Excellent (>85%), Good (>70%), Fair (>50%), Needs Improvement (<=50%).

## Optional AI Enhancement Layer
* **Local Open-Source AI (Primary):** Fast, CPU-safe inference using quantized GGUF models (`Qwen2.5-0.5B-Instruct-GGUF` via `llama-cpp-python`). No API key or internet access required.
* **Gemini API (Optional):** REST API integration for Gemini 1.5 Flash when `GEMINI_API_KEY` is configured.
* **AI Features:**
  - Resume bullet optimization (`ai/resume_improver.py`)
  - Semantic job description parsing (`ai/jd_semantic_parser.py`)
* **Independence Guarantee:** Core ATS evaluation, scoring, and PDF generation function completely offline without any AI runtime.

## Testing & Verification
* **Test Suite:** 163 unit, integration, and benchmark tests across 13 test modules in `tests/`.
* **CI/CD:** Automated GitHub Actions workflow (`.github/workflows/ci.yml`) running all test suites on pull requests and pushes to main.

## Deployment Architecture
* **Container:** Multi-stage lightweight Docker image (`python:3.12-slim`) running Waitress WSGI on non-root user.
* **Cloud Target:** Render.com Infrastructure-as-Code via `render.yaml` with automated health check probe (`/health`).
