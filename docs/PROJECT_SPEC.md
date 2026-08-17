# ResumeIQ Project Specification

## Project Goal
ResumeIQ (ATS Resume Evaluator) is an intelligent application designed to analyze and score resumes against specific job descriptions. It provides detailed feedback, skill gap analysis, and tailored job recommendations by simulating standard Applicant Tracking Systems (ATS) combined with advanced semantic matching.

## Architecture
**CURRENT**
* **Backend:** Flask application (`app.py`) handling file uploads, text parsing, and routing.
* **Core Processing:** Custom matching engine (`matcher.py`) and text similarity (`text_similarity.py`).
* **Skill Engine:** A modularized Python-based dictionary architecture located in the `skills/` directory.
* **Machine Learning:** `scikit-learn` for TF-IDF (lexical) and `sentence-transformers` for semantic embeddings.
* **Reporting:** `reportlab` for generating downloadable PDF reports.

**PLANNED**
* Improved abstraction for data persistence (transitioning from hardcoded dicts to a proper database or structured document store if required).

**FUTURE**
* Containerization (Docker) and Cloud-native deployment architecture.

## ATS Matching Pipeline
**CURRENT**
1. **Parsing:** Extracts text from uploaded PDF/DOCX resumes.
2. **JD Segmentation:** Splits the Job Description into sections (general, required, optional, responsibilities) based on keyword headers.
3. **Extraction:** Identifies skills, alternative requirements, experience, and education keywords.
4. **Scoring:** Calculates scores for text similarity, skill matches, and experience.
5. **Aggregation:** Combines sub-scores into a final weighted ATS match score.
6. **Reporting:** Renders a web dashboard and generates a downloadable PDF.

## Skill Database Architecture
**CURRENT**
* **Modularization:** Factored into domains (e.g., `programming.py`, `cloud.py`, `frontend.py`) unified in `skills/__init__.py`.
* **Normalization:** Enforces canonical naming, category, and default priority for each skill.
* **Alias Handling:** Automatically builds an alias index and removes ambiguous aliases that map to multiple canonical skills.
* **Related Skills:** Supports defining related skills to expand potential matches.

## JD Skill Extraction
**CURRENT**
* Preprocesses text, preserving domain-specific characters (e.g., `C++`, `Node.js`).
* Extracts canonical skills using boundary patterns.
* Resolves overlapping mentions by preferring the longest alias/canonical match.
* Evaluates parenthetical context to ignore descriptive skills within OR-conditions (e.g., "Node.js (TypeScript) or Go" extracts Node.js and Go, ignoring TypeScript as a requirement).

## OR-Condition Matching
**CURRENT**
* Detects alternative skill requirements separated by "or" or slashes (e.g., "AWS or GCP", "Python / Go").
* Groups alternative skills into a single requirement block.
* Scored collectively: matching any skill in the OR-group fulfills the requirement for the group.

## Skill Matching
**CURRENT**
* Compares extracted resume skills against extracted JD skills.
* Calculates a weighted skill score: Required skills (3 pts), General skills (2 pts), Optional skills (1 pt).

## Semantic/Text Similarity
**CURRENT**
* **Lexical:** TF-IDF vectorization with cosine similarity.
* **Semantic:** `SentenceTransformer` (`all-MiniLM-L6-v2`) embeddings with cosine similarity.
* **Hybrid Score:** Combines Semantic (70%) and Lexical (30%) scores into a unified similarity percentage.

## Experience Scoring
**CURRENT**
* Heuristics-based extraction of experience durations (years, months, days) using regex patterns.
* Detects student experience keywords (intern, research, project).
* Calculates a capped baseline score based on the highest extracted experience time.

## Final ATS Scoring
**CURRENT**
* Weighted Aggregation: Skill Match (50%) + Text Similarity (30%) + Experience Score (20%).
* Categorizes the fit based on thresholds: Excellent (>85%), Good (>70%), Fair (>50%), Needs Improvement (<=50%).

## Report Generation
**CURRENT**
* Generates stylized PDF reports using `reportlab`.
* Includes ATS Score, matched/missing skills, suggestions, and job recommendations.

## Frontend/Report UX
**CURRENT**
* Flask templates rendering interactive web views (`landing.html`, `analyze.html`, `dashboard.html`).
* Displays visual breakdown of scores and skill gaps.

## Performance Optimization
**CURRENT**
* Uses `functools.lru_cache` to keep the Semantic model in memory.
* Vectorized operations using scikit-learn and sentence-transformers.

**PLANNED**
* Asynchronous processing for model inference and PDF generation to prevent blocking the Flask main thread.

## Database Factorization
**CURRENT**
* Refactored a monolithic database into granular, domain-specific modules inside the `skills/` package.

## Testing/Evaluation
**PLANNED**
* Comprehensive Unit Testing for regex extractions, OR-condition logic, and scoring math.
* Integration Testing for the Flask application.
* Evaluation dataset to measure accuracy of ATS scoring against human-rated resumes.

## Deployment
**PLANNED**
* Creation of Dockerfile.
* Setup of CI/CD pipeline.

**FUTURE**
* Cloud deployment (AWS/GCP/Azure).

## Future AI/ML Capabilities
**FUTURE**
* Generative AI integration to rewrite resume bullets.
* LLM-based intelligent JD parsing instead of regex heuristics.
* Semantic mapping of related skills (e.g., partial credit for knowing React when Vue is requested).
