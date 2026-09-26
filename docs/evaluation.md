# Evaluation & Experimentation Framework Documentation

> **Scope Statement:** ELHGS is an AI-assisted livestock health and condition grading system that provides explainable recommendations using non-identifiable images and measurable health attributes. It supports human graders and never replaces expert judgment.

This document defines the statistical evaluation framework, experiment methodology, error taxonomy, and report generation pipeline for the Explainable Livestock Health Grading System (ELHGS).

---

## 1. Controlled Experiment Design

To evaluate the degree to which AI assistance can reduce inter-rater friction:
- **Baseline (Arm 1):** Two unassisted human graders independently evaluate identical livestock samples.
- **Assisted (Arm 2):** Human graders evaluate identical samples guided by ELHGS Rule Engine recommendations and plain-text reasoning.

### Evaluated Benchmark Impact (Simulated Baseline)
- **Disagreement Reduction:** **71.8% drop in inter-grader disputes** `[simulated, experiment_runner.py in-silico trial, N=200]`.
- **Evaluation Speed:** **67.3% reduction in review time per head** (5.2 mins -> 1.7 mins) `[simulated, experiment_runner.py in-silico trial, N=200]`.
- **Human Authority:** 100% preservation of human final decisions during disagreements.

> [!IMPORTANT]
> **Audit Notice:** The 71.8% dispute reduction and 67.3% time savings are derived from an algorithmic simulation modeling subjective grader variance under synthetic conditions. Genuine real-world dispute reduction requires a prospective, randomized field study across live auction yards or ranches, which is currently pending field cohort deployment.

---

## 2. Real-World Evaluation Framework (`real_dataset_runner.py`)

When genuine ethically sourced imagery and double-blind expert labels are ingested:
1. Evaluates Rule Engine, Decision Tree, and Logistic Regression on held-out test splits without data leakage.
2. Generates: Accuracy, Macro Precision, Macro Recall, Macro F1, Cohen's Kappa, Exact Match %, Adjacent Match %, Confusion Matrices, and Confidence Distributions.
3. Persists complete experiment metadata to the PostgreSQL `experiment_results` table.
4. Returns explicit `PENDING_REAL_DATA` when genuine expert consensus samples are pending.

---

## 3. Statistical Metrics & Formulas

| Metric | Formula / Calculation Method |
| :--- | :--- |
| **Accuracy** | $\frac{TP + TN}{TP + TN + FP + FN}$ |
| **Macro Precision** | Unweighted mean of precision across classes A, B, C, D |
| **Macro Recall** | Unweighted mean of recall across classes A, B, C, D |
| **Macro F1-Score** | Harmonic mean of Macro Precision and Macro Recall |
| **Cohen's Kappa ($\kappa$)** | $\frac{P_o - P_e}{1 - P_e}$ (Agreement corrected for hypothetical chance) |
| **Exact Agreement %** | Percentage of samples where grades match identically |
| **Adjacent Agreement %** | Percentage of samples where grades differ by at most one tier (e.g. A vs B) |

---

## 4. Error Taxonomy

Prediction errors and disagreements are classified into 5 categories:
1. **Borderline BCS Case:** BCS falls on threshold boundary (2.0, 2.5, 3.5, 4.0).
2. **Missing Attributes:** Incomplete observation input (penalizes confidence score).
3. **Rule Threshold Conflict:** Multiple sub-grades triggering competing rule hierarchy branches.
4. **Expert Disagreement:** Inter-annotator variance between expert grader 1 and grader 2.
5. **Poor Image Quality:** Image failed resolution, lighting, or framing standards.

---

## 5. Generated Artifacts & Reports
- `reports/experiment_report.md`
- `reports/comparison_report.md`
- `reports/metrics_report.md`
- `reports/stakeholder_validation.md`
- `reports/limitations_report.md`
