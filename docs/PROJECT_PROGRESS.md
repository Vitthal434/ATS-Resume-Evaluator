# ResumeIQ Project Progress

This document tracks the stage-wise backlog for the ResumeIQ ATS Evaluator project.

**Legend:**
* `[x]` = Implemented AND verified in local codebase
* `[ ]` = Unfinished / Not yet verified

---

## Stage 1: Core Parsing & Text Processing
* `[x]` Resume text extraction (PDF & DOCX parsing via `resume_parser.py`)
* `[x]` Basic Job Description text normalization
* `[x]` Lexical text similarity scoring (TF-IDF via `text_similarity.py`)
* `[x]` Semantic text similarity scoring (`SentenceTransformer` in `matcher.py`)
* `[x]` Hybrid text similarity scoring (70% Semantic, 30% Lexical)

### Stage 1 Validation Results — 2026-08-17

Test suite: `tests/test_scoring_validation.py` — **15/15 tests passed** (`Ran 15 tests in 43.607s — OK`).

| TC | Description | Key Result | Status |
|----|-------------|------------|--------|
| TC-01 | Identical resume/JD | ATS: 97.6%, Skill: 100%, TextSim: 100% | PASS |
| TC-02 | Frontend resume vs Frontend JD | ATS: 86.35%, Skill: 100%, TextSim: 54.5% | PASS |
| TC-03 | Unrelated resume vs Frontend JD | ATS: 26.32%, Skill: 0%, Matched: [] | PASS |
| TC-04 | Empty resume | ATS: 10.0%, Skill: 0%, Matched: [] | PASS |
| TC-05 | Empty JD | ATS: 20.0%, Skill: 0 | PASS |
| TC-06 | Frontend vs Frontend (skill detail) | Skill: 100%, Matched: js/ts/react/html/css/jest/webpack/git/rest api | PASS |
| TC-07 | Backend vs Backend (skill detail) | Skill: 90.48%, Missing: kafka or rabbitmq, kubernetes | PASS |
| TC-08 | ML/NLP vs ML/NLP (skill detail) | Skill: 95.65%, Missing: dvc or mlflow | PASS |
| TC-09 | Frontend vs Backend (cross-domain) | Skill: 14.29%, Matched: rest api only | PASS |
| TC-10 | Backend vs ML (cross-domain) | Skill: 17.39%, Matched: docker, python | PASS |
| TC-11 | Alias canonicalization | py→python, js→javascript, sklearn→scikit-learn, nlp→NLP, etc. all OK | PASS |
| TC-12 | Missing required skills | Skill: 0%, full required skills listed as missing | PASS |
| TC-13 | Optional / nice-to-have parsing | Required OR-alts: {go,python},{django,fastapi}; Optional OR-alts: {aws,gcp},{kafka,rabbitmq} | PASS |
| TC-14 | Experience scoring | 5yr→100%, 18mo→74%, intern→65%, none→50% | PASS |
| TC-15 | Weighted ATS arithmetic | Reported: 82.96% = Recomputed: 82.96% | PASS |

## Stage 2: Skill Engine & Database Refactor
* `[x]` Migrate monolithic skill list to modular database (`skills/` directory)
* `[x]` Skill normalization (canonical names, priorities, categories)
* `[x]` Alias resolution and ambiguous alias conflict handling
* `[x]` Canonical skill extraction using boundary regex patterns

### Stage 2A Evaluation: Text Similarity — 2026-08-17

Test suite: `tests/test_text_similarity_eval.py` — **13/13 tests passed** (`Ran 13 tests in 9.502s — OK`).

**Algorithm in production:** `matcher.calculate_text_similarity()` — hybrid 70% SentenceTransformer + 30% TF-IDF.

**Note:** `matcher.py` previously contained a dead import (`from text_similarity import calculate_text_similarity`), which was shadowed by the local hybrid definition. This dead import was cleaned up in Stage 2B (see IFU-05).

### Stage 2B Cleanup: Dead Import Resolution — 2026-08-17
* Removed obsolete/shadowed import `from text_similarity import calculate_text_similarity` from `matcher.py`.
* Preserved `text_similarity.py` as an independent TF-IDF module for standalone use.
* Verified that production scoring behavior and hybrid similarity calculation remain 100% unchanged (`test_text_similarity_eval.py` 13/13 OK, `test_scoring_validation.py` 15/15 OK).

| TC | Description | Score | Reasonable? |
|----|-------------|-------|-------------|
| TC-ST-01 | Identical texts (JD_FRONTEND as both) | 100.0% | Yes — expected |
| TC-ST-02 | Nearly identical, reworded | 74.87% | Yes — semantic handles paraphrasing |
| TC-ST-03 | Frontend resume vs Frontend JD | 54.86% | Yes — strong same-domain overlap |
| TC-ST-04 | Backend resume vs Frontend JD (partial) | 32.71% vs 54.86% ref | Yes — correctly lower |
| TC-ST-05 | Frontend resume vs DevOps JD (diff role) | 32.20% vs 54.86% ref | Yes — correctly lower |
| TC-ST-06 | Construction resume vs Frontend JD | 21.36% | Yes — unrelated |
| TC-ST-07 | Empty resume | 0.0% | Yes — guard fires |
| TC-ST-08 | Empty JD | 0.0% | Yes — guard fires |
| TC-ST-09 | Skills-only resume vs detailed JD | 26.59% vs 54.86% ref | Watch — TF-IDF penalises brevity |
| TC-ST-10 | Detailed resume vs skills-only JD | 45.31% vs 54.86% ref | Yes — asymmetry is modest |
| TC-ST-11 | Stability (3 repeated calls, ML/NLP pair) | 56.2% / 56.2% / 56.2% | Yes — fully deterministic |
| TC-ST-12 | Cross-domain ordering (3x3 matrix) | All 3 same-domain pairs highest | Yes — correct ordering |
| TC-ST-13 | Hybrid vs TF-IDF-only on same input | 54.86% vs 28.02% | Yes — confirms two distinct functions |

**Observed similarity ranges:**
- Identical: ~100%
- Same-domain resume/JD: 54–59%
- Cross-domain (related SW): 23–33%
- Unrelated domain: ~21%
- Empty: 0%

## Stage 3: Advanced JD Requirements Matching
* `[x]` JD section extraction (Required, Optional, Responsibilities)
* `[x]` OR-condition alternative grouping (e.g., "Python or Go")
* `[x]` Ignore parenthetical descriptors in OR-conditions
* `[x]` Weighted skill scoring (Required = 3, General = 2, Optional = 1)
* `[x]` Experience extraction and scoring heuristics
* `[x]` Education keyword extraction

## Stage 4: Scoring & Application Logic
* `[x]` Final ATS Scoring algorithm (50% Skill, 30% Text, 20% Experience)
* `[x]` Fit categorization (Excellent, Good, Fair, Needs Improvement)
* `[x]` Job recommendation matching based on matched skills
* `[x]` Suggestion generation (missing skills, experience highlights)

## Stage 5: Reporting & Frontend UX
* `[x]` Flask web application routing and controllers (`app.py`)
* `[x]` HTML template rendering (Landing, Analyze, Dashboard)
* `[x]` PDF Report Generation (`report_generator.py` using `reportlab`)
* `[x]` Report download endpoint

## Stage 6: Testing & Evaluation (PLANNED)
* `[ ]` Unit test suite for `matcher.py` logic
* `[ ]` Unit test suite for `skills` module resolution
* `[ ]` Evaluation dataset generation for accuracy tuning
* `[ ]` Integration tests for API endpoints

## Stage 7: Optimization & Refactoring (PLANNED)
* `[ ]` Asynchronous job queue for model inference
* `[ ]` Optimized caching for model loading and scoring requests

## Stage 8: Deployment & Cloud (FUTURE)
* `[ ]` Dockerization (Dockerfile & docker-compose)
* `[ ]` CI/CD Pipeline integration (GitHub Actions)
* `[ ]` Cloud hosting deployment

## Stage 9: Advanced AI Capabilities (FUTURE)
* `[ ]` LLM-driven resume bullet optimization
* `[ ]` LLM-driven complex JD semantic parsing
* `[ ]` Partial credit matching for related/transferable skills

---

## Issues / Follow-ups

### IFU-01 — Empty resume produces ATS score of 10.0%, not 0% [RESOLVED]
**Observed:** `final_match_score("", JD_FRONTEND)` originally returned `ats_score = 10.0` due to baseline experience fallback.
**Fix:** Added guard `if not resume or not resume.strip(): return 0` in `experience_score()`. Empty/blank resumes now yield `skill_score = 0`, `text_similarity = 0`, `experience_score = 0`, and `ats_score = 0.0`. Verified in TC-04 test suite.

### IFU-02 — Duplicate entries in missing_skills output [RESOLVED]
**Observed:** `missing_skills` could contain duplicate entries when skills appeared both individually and as part of an OR-group.
**Fix:** Added order-preserving deduplication (`missing_skills = list(dict.fromkeys(missing_skills))`) before returning from `calculate_skill_match()`.

### IFU-03 — Test harness Unicode encoding [RESOLVED]
**Cause:** The `→` (U+2192) character in `_report` / `_flag` f-strings caused `UnicodeEncodeError` on Windows cp1252 console.
**Fix applied:** Replaced `→` and `⚠` with ASCII `->` and `[SUSPICIOUS]` in `tests/test_scoring_validation.py`.

### IFU-04 — `sentence-transformers` missing from requirements.txt [RESOLVED]
**Fix:** Added `sentence-transformers` to `requirements.txt`.

### IFU-05 — Dead import: `text_similarity.calculate_text_similarity` is shadowed [RESOLVED]
**Observed (TC-ST-13):** `matcher.py` line 19 imported `calculate_text_similarity` from `text_similarity.py`. However, line 705 defined a *local* function with the same name, which immediately shadowed the import at module scope.
**Fix:** Removed the dead import `from text_similarity import calculate_text_similarity` from `matcher.py` and cleaned up unused import in `tests/test_scoring_validation.py`. Preserved `text_similarity.py` in codebase. Verified all 28 tests across both test suites pass with identical scores.
