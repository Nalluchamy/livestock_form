# 🚀 Release Notes - ELHGS v1.1.0 & v1.0.0

> **Scope Statement:** ELHGS is an AI-assisted livestock health and condition grading system that provides explainable recommendations using non-identifiable images and measurable health attributes. It supports human graders and never replaces expert judgment.

---

## 🌟 Release v1.1.0 — Phase 11 Production Data & Real-World Validation Upgrade

### New Features & Enhancements
1. **Real Dataset Infrastructure (`dataset/real/`):** Segregated raw, processed, labels, splits, and documentation directories. Integrated dataset ingestion pipeline with image format validation, SHA-256 and perceptual dHash duplicate detection, and Pillow-based EXIF/GPS scrubbing.
2. **Double-Blind Expert Annotation Schema:** Enforced schema supporting missing attributes and preserving inter-expert disagreements without artificial consensus.
3. **Leakage-Safe Dataset Splitting:** Implemented group-aware splitting ensuring all observations of the same animal reside in one partition with cross-split duplicate prevention.
4. **Persistent PostgreSQL Disagreement Reviews (`disagreement_reviews`):** Full lifecycle management (`PENDING`, `IN_REVIEW`, `RESOLVED`, `ESCALATED`, `CANCELLED`) with guaranteed immutability of original human and system grades and clinical resolution audit trails.
5. **Persistent Experiment Tracking (`experiment_results`):** Automated persistence of benchmark runs, per-model accuracy, precision, recall, F1, Cohen's Kappa, and confusion matrices.
6. **Dynamic Dashboard & Senior Review Queue:** Upgraded React pages with live backend metrics, zero hardcoding, and transparent pending status badges.
7. **Authentic Stakeholder Validation Protocol:** Established formal 8-dimension intake protocol and blank collection templates with zero fabricated persona data.
8. **Expanded Test Suite:** 65 passing tests (100% pass rate) covering ingestion, splitting, schemas, persistence, and REST APIs.

---

## 🌟 Release v1.0.0 — Hackathon Foundation
- **Deterministic Rule Engine Baseline:** Evaluates BCS (1.0–5.0), coat, eyes, wounds, mobility, and appetite to produce Grade A-D with plain-text explanation reasons.
- **Advisory Machine Learning Layer:** White-box Decision Tree Classifier (88.17% Acc [measured, 600 synthetic samples]) and Logistic Regression.
- **Human-in-the-Loop & Disagreement Tracking:** Senior Review escalation without overwriting human authority.
- **Offline-First PWA:** Full offline functionality with IndexedDB and two-stage sync.
- **Privacy by Design:** Automatic client-side canvas and server-side EXIF stripping.
