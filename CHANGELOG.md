# Changelog

All notable changes to the ResumeIQ project will be documented in this file.

This project follows a concise changelog format inspired by [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] - 2026-08-18

### Added
- **Deterministic ATS Scoring Engine:** Authoritative multi-component scoring (50% Skill Match, 30% Hybrid Text Similarity, 20% Experience Match) operating completely offline.
- **Hybrid Text Similarity:** 70% SentenceTransformer semantic embeddings (`all-MiniLM-L6-v2`) combined with 30% TF-IDF lexical vectorization.
- **Skill Engine & Alias Canonicalization:** Modularized 14-domain skill database with canonical resolution, alias indexing, and collective OR-group evaluation.
- **Partial Credit Skill Matching:** Conservative intra-domain 50% partial credit matching for related and transferable skills.
- **Intelligent Gap Analysis & Career Roadmap:** Deterministic skill gap prioritization with urgency tiers, time-to-acquire estimates, and action steps.
- **Job Recommendation System:** Domain-aware career pathway suggestions mapped to extracted canonical candidate skills.
- **Local Open-Source AI Provider:** High-performance, CPU-optimized local inference via `llama-cpp-python` with quantized GGUF models (`Qwen2.5-0.5B-Instruct-GGUF`), alongside optional Gemini REST API provider.
- **Optional AI Enhancements:** Non-hallucinating resume bullet optimization and complex semantic job description parsing.
- **Visual PDF Report Generator:** Multi-page branded ReportLab PDF generator featuring metric scorecards, skill badge grids, and career roadmaps.
- **Modern Web Dashboard & UI Polish:** Responsive Bootstrap 5 interface with hero section, sample preloads, real-time match visualization, and async AI actions.
- **Comprehensive Verification Suite:** 163 unit, integration, and dataset benchmark tests with 100% pass rate across 13 test modules.
- **Production Deployment & CI/CD:** Production `Dockerfile`, `docker-compose.yml`, Waitress WSGI entrypoint (`wsgi.py`), Render Blueprint (`render.yaml`), and GitHub Actions CI pipeline.
