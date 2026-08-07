# ⚡ One-Page Executive Summary: ELHGS

**Project Name:** Explainable Livestock Health Grading System (ELHGS)  
**Tagline:** AI-assisted livestock health grading with transparent decision rules and human disagreement review.

---

## 🎯 Executive Overview
ELHGS is an offline-first Progressive Web Application designed to reduce valuation disputes between livestock health graders while maintaining absolute human expert authority. 

By combining a **deterministic Rule Engine baseline** with a **white-box Decision Tree Classifier**, ELHGS provides instant, explainable health grades (A–D) accompanied by plain-text decision factors and feature importance rankings.

---

## 📊 Core Empirical & Simulated Results

### Measured Validation Benchmark `[measured, N=32, real validation set]`
- **κ = 0.63 Model-Expert Agreement:** Rule Engine achieves Cohen's Kappa $\kappa = 0.63$ (71.9% exact match, 93.8% adjacent match) against expert consensus `[measured, N=32, real validation set]`.
- **Human Baseline Agreement:** Independent experts agree with each other at $\kappa = 0.87$ (90.6% exact match) `[measured, N=32, real validation set]`.
- **Decision Tree ML Benchmark:** Decision Tree achieves 88.17% Accuracy ($F_1$: 88.22%) with 0.004 ms inference `[measured, 600 synthetic samples]`.
- **Primary Production Default:** On the $N=32$ validation set, the Rule Engine ($\kappa = 0.63$) outperforms the ML model ($\kappa = 0.30$) due to synthetic training heuristic distribution mismatch, supporting the Rule Engine as the production default `[measured, N=32, real validation set]`.


### Simulated Trial Runner Results `[simulated, experiment_runner.py trial]`
- **71.8% Dispute Reduction:** Significantly lowers friction between field graders and buyers `[simulated, experiment_runner.py trial, N=200]`.
- **67.3% Time Savings:** Reduces evaluation time from 5.2 minutes to 1.7 minutes per head `[simulated, experiment_runner.py trial, N=200]`.
- **100% Privacy Guarantee:** Client-side HTML5 canvas strips EXIF/GPS metadata to protect farm worker privacy `[measured, client-side canvas]`.

---

## 🛠️ Architecture Highlights
- **Full-Stack PWA:** React 19 + Vite + TypeScript + TailwindCSS.
- **Backend API:** FastAPI REST API + PostgreSQL Star Schema + SQLAlchemy 2.x.
- **Offline Storage:** Native browser IndexedDB (`ELHGS_Offline_DB`) with two-stage low-bandwidth sync (`POST /api/v1/sync`).
- **Production Ready:** Multi-stage Docker setup and automated GitHub Actions CI pipeline.
