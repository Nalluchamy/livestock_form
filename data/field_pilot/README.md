# Field Pilot Survey Registry & Data Directory

> **PILOT STATUS: PENDING GENUINE STAKEHOLDER COHORT EXECUTION**
>
> In accordance with the Phase 12 primary objective and zero-fabrication research integrity standards, all operational infrastructure, survey templates, and informed consent protocols have been fully implemented. Field execution is pending live participant intake.

## Directory Contents

- `pilot_feedback_template.json`: Structured schema for individual evaluator survey submissions.
- `pilot_feedback_template.csv`: Tabular layout for aggregate analysis of evaluator ratings.
- Incoming completed feedback files should be saved under `data/field_pilot/responses/{pilot_run_id}_{evaluator_id}.json`.

## Evaluation Criteria Tracked

1. **Rubric Clarity (1–5):** Comprehensiveness and unambiguity of Cattle Rubric v2.0.
2. **Photo-Visible Separation (1–5):** Feasibility and adherence to evaluating only photo-visible traits from photos.
3. **Appetite Non-Inference Feasibility (1–5):** Ease of sourcing bunk intake/management logs.
4. **System Responsiveness (1–5):** Speed of image ingestion, sanitization, and inferencing.
5. **Offline Reliability (1–5):** IndexedDB queue stability and sync integrity in remote pasture/pen environments.
6. **Explainability Helpfulness (1–5):** Utility of deterministic explanation strings during review.
7. **Clinical Safety Protocol (1–5):** Clarity of urgent escalation alerts and veterinary disclaimer.
