# ⚠️ System Limitations & Risk Register

This document outlines known limitations, potential bias risks, and future improvement roadmaps for the ELHGS platform.

---

## 1. Documented Limitations

### A. Synthetic Dataset Constraints
- **Limitation:** Phase 6 machine learning models were trained on 600 synthetic livestock observation records.
- **Impact:** Models may require fine-tuning on larger real-world empirical datasets prior to commercial deployment.

### B. Image Upload in Low-Bandwidth Mode
- **Limitation:** On 2G/3G networks, attribute JSON is synced immediately, but raw photos are queued for later upload.
- **Impact:** Senior Reviewers inspecting a remote disagreement may temporarily lack high-res photos until the device re-connects to broadband.

---

## 2. Bias & Safety Guardrails

| Risk Area | Mitigation Strategy | Enforcement |
| :--- | :--- | :--- |
| **Worker Surveillance Risk** | Automatic EXIF/GPS stripping before upload | Built-in `imageOptimizer.ts` |
| **Automation Bias** | Human-in-the-loop policy; AI cannot overwrite human grade | Enforced in `grading_service.py` |
| **Overconfidence Risk** | Confidence penalized for missing data & contradictions | Enforced in `confidence.py` |
