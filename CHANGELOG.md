# Changelog

All notable changes to the Explainable Livestock Health Grading System (ELHGS) project will be documented in this file.

## [1.0.0] - 2026-08-06

### Added
- **Phase 1:** Project scaffolding, system context diagrams, Docker base structure, and coding standards.
- **Phase 2:** PostgreSQL Star Schema (`dim_sample`, `dim_grader`, `dim_image`, `dim_criterion`, `fact_grading_events`) and Alembic migration scripts.
- **Phase 3:** Deterministic Rule Engine, confidence scoring, plain-text explanation generator, and human disagreement detector.
- **Phase 4:** FastAPI REST API endpoints (`/health`, `/grade`, `/grading-events`, `/disagreements`, `/metrics`), repository layer, request ID & logging middlewares, and DEMO_MODE support.
- **Phase 5:** React 19 + Vite + TypeScript + TailwindCSS PWA frontend with Civic Color Palette and responsive mobile navigation.
- **Phase 6:** Explainable Machine Learning Layer featuring Decision Tree Classifier (88.17% Acc [measured, 600 synthetic samples]) and Logistic Regression, model registry, and 3-way comparative benchmarks.
- **Phase 7:** Offline-first PWA with Service Worker, IndexedDB queue (`ELHGS_Offline_DB`), client-side canvas EXIF privacy stripper, low-bandwidth two-stage sync engine, and `POST /sync` API.
- **Phase 8:** 2-arm simulation experiment framework (71.8% dispute reduction, 67.3% time savings), error taxonomy analyzer, and automatic markdown report generator in `reports/`.
- **Phase 9:** Production multi-stage Dockerfiles, GitHub Actions CI workflow (`ci.yml`), deployment guides, user/admin guides, and hackathon final checklist.
