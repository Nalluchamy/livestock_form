# 👥 ELHGS Stakeholder Validation Protocol

> **Scope Statement:** ELHGS is an AI-assisted livestock health and condition grading system that provides explainable recommendations using non-identifiable images and measurable health attributes. It supports human graders and never replaces expert judgment.

| Document Attribute | Specification |
|:---|:---|
| **Protocol Version** | 1.0.0 (Phase 11 Production Data Upgrade) |
| **Status** | Active Field Intake Protocol — Real Cohort Intake Pending |
| **Target Participants** | Consenting livestock farmers, certified field graders, veterinary auditors, senior reviewers |
| **Primary Objective** | Empirically validate explainability clarity, advisory utility, non-punitive posture, and offline usability |

---

## 1. Ethical Governance & Anonymity

1. **Informed Consent:** Prior to evaluating the system, all participants must execute the standard informed consent agreement covering data usage, non-punitive guarantees, and voluntary withdrawal.
2. **De-Identification & Pseudonymization:** To prevent workplace surveillance, employer retaliation, or commercial bias, all participant identities are strictly mapped to anonymous role-based tokens:
   - `STK-FARM-###`: Livestock Farm Owner / Operator
   - `STK-GRD-###`: Certified Field Grader / Inspector
   - `STK-VET-###`: Licensed Veterinary Professional
   - `STK-AUD-###`: Senior Review Auditor
3. **Data Segregation:** Real stakeholder survey responses are stored exclusively in `data/stakeholder_feedback/`. No simulated or demonstration responses may ever be co-mingled with genuine evaluation submissions.
4. **Prohibition of Fabrication:** No participant names, credentials, qualitative quotes, or Likert ratings may be fabricated or imputed by AI. If a cohort has not yet completed the evaluation, the report status must remain **PENDING REAL-WORLD VALIDATION**.

---

## 2. Structured 8-Dimension Evaluation Framework

Participants evaluate ELHGS after completing at least 5 live or simulated evaluation workflows:

### Dimension 1: Explanation Clarity (Likert 1–5)
- *Prompt:* "The plain-text explanations clearly articulated the specific physical attributes (BCS, coat, eyes, mobility, wounds) driving the recommended grade."
- *Scale:* 1 (Completely opaque / confusing) to 5 (Crystal clear and actionable).

### Dimension 2: Grading Recommendation Usefulness (Likert 1–5)
- *Prompt:* "The AI recommendation served as a valuable advisory reference during condition assessment."
- *Scale:* 1 (Not useful / misleading) to 5 (Highly valuable advisory support).

### Dimension 3: Confidence-Score Usefulness (Likert 1–5)
- *Prompt:* "The displayed confidence score provided meaningful insight into observation completeness and ambiguity."
- *Scale:* 1 (Misleading / arbitrary) to 5 (Highly informative of data quality).

### Dimension 4: Disagreement Workflow (Likert 1–5)
- *Prompt:* "The process for flagging disagreements for Senior Review felt transparent, respectful of grader autonomy, and non-punitive."
- *Scale:* 1 (Punitive / cumbersome) to 5 (Seamless and protective of human authority).

### Dimension 5: Usability & Ergonomics (Likert 1–5)
- *Prompt:* "The mobile-first user interface allowed fast and accurate attribute selection in pen/field conditions."
- *Scale:* 1 (Difficult / slow) to 5 (Effortless and highly responsive).

### Dimension 6: Offline Functionality (Likert 1–5)
- *Prompt:* "The offline caching and synchronization mechanism reliably recorded evaluations without active network connectivity."
- *Scale:* 1 (Unreliable / data loss) to 5 (Flawless offline operation).

### Dimension 7: Perceived Trust & Assistive Posture (Likert 1–5)
- *Prompt:* "Did this system feel like an assistive copilot that respects human authority, or an automated judge?"
- *Scale:* 1 (Feels like surveillance / judging) to 5 (Feels purely supportive / non-punitive).

### Dimension 8: Suggested Improvements & Qualitative Critique (Open Text)
- *Prompt:* "Detail specific feature gaps, physical attribute omissions, or operational bottlenecks encountered during evaluation."

---

## 3. Data Collection Templates

- Machine-readable JSON template: `data/stakeholder_feedback/feedback_template.json`
- Tabular CSV template: `data/stakeholder_feedback/feedback_template.csv`
- Submissions must include: `participant_id`, `role`, `timestamp`, numeric scores for D1–D7, and qualitative text for D8.
