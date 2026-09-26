# STAKEHOLDER VALIDATION PROTOCOL & FIELD PILOT REPORT (STAGE 2)

## 1. Study Purpose & Scope

To validate the Explainable Produce Quality Grading System with real agricultural practitioners, a targeted usability and acceptance study was designed for farm managers, packhouse supervisors, and professional quality graders.

The evaluation assesses four core operational dimensions:
1. **Explainability & Transparency**: Whether rule-based justifications and attribute breakdowns make sense to agricultural practitioners.
2. **Operational Ergonomics**: Speed, ease of image capture, and usability on mobile devices under packhouse lighting.
3. **Disagreement Resolution**: Whether double-blind annotation and persistent adjudication build trust and eliminate subjective conflict.
4. **Field Resilience**: Usability of offline drafting and synchronization under intermittent cellular connectivity.

---

## 2. Participant Consent & Ethical Safeguards

### 2.1. Ethical Statement
Participation in this study is strictly voluntary. Data collected is anonymous and used solely to refine software usability and grading transparency.

### 2.2. Consent Form Template

```markdown
INFORMED PARTICIPANT CONSENT FORM: EXPLAINABLE QUALITY GRADING SYSTEM (EQGS)

Project: Antigravity Explainable Produce Quality Grading Pilot (Stage 2)
Investigator: Agricultural AI Research & Engineering Team

1. Nature and Purpose: You are invited to test an explainable software tool designed to assist in grading fresh produce (tomatoes) and managing grader disagreements.
2. Voluntary Participation: Your participation is entirely voluntary. You may decline to answer any question or discontinue participation at any time without penalty or impact on your employment.
3. Non-Punitive & Non-Surveillance Commitment: This system does not track your grading speed for workplace pacing, does not rank workers against each other, and does not capture biometric/facial data.
4. Data Privacy: Your responses will be identified only by an anonymized participant code (e.g., P-01). No personally identifiable information or proprietary farm commercial data will be published.
5. Consent Confirmation:
   "I have read and understood the information above. I agree to participate in this usability study."

   Participant Signature / Confirmation: _______________________
   Date: ________________________
```

---

## 3. Evaluation Tasks Protocol

Participants execute five structured tasks using a mobile smartphone or tablet:

| Task ID | Task Description | Success Criteria |
| :--- | :--- | :--- |
| **Task 1** | Capture/upload a tomato image with neutral background; observe blur/lighting check. | Quality check accurately accepts sharp photo or flags blurred test image. |
| **Task 2** | Review the automated feature extraction (defect %, ripeness stage, shape circularity) and generated provisional grade. | Participant can read and articulate why the system suggested Grade A, B, or C. |
| **Task 3** | Submit an independent quality grade under double-blind isolation. | Submission succeeds without displaying concurrent grader's entry. |
| **Task 4** | Act as Senior Reviewer on an adjudicated disagreement case. | Reviewer accesses both original grades, examines image evidence, and logs resolution. |
| **Task 5** | Switch device to Offline/Airplane mode, submit a local grading record, restore connectivity, and verify sync. | Record queues locally in IndexedDB and syncs to backend upon reconnection. |

---

## 4. Standardized Usability Survey Instrument

Participants score five statements on a 5-point Likert scale (1 = Strongly Disagree, 5 = Strongly Agree):

1. **$Q_1$ (Usability)**: "The grading interface was straightforward to navigate on a mobile screen."
2. **$Q_2$ (Explanation Clarity)**: "The rule explanations clearly showed me why a specific grade was assigned."
3. **$Q_3$ (Attribute Accuracy)**: "The measured surface defect percentage and color stage aligned with my visual judgment."
4. **$Q_4$ (Disagreement Fairness)**: "The double-blind review process provides a fair, unbiased method to resolve grader differences."
5. **$Q_5$ (Packhouse Viability)**: "The offline queue and local saving make this tool practical for remote packhouses with weak connectivity."

### Qualitative Feedback Questions:
- *What specific information was missing from the grading explanation?*
- *In what scenarios would you override the system's provisional grade?*
- *What features or changes would make this tool faster during high-volume harvest days?*

---

## 5. Study Execution Status & Transparency Declaration

> [!WARNING] Stakeholder Validation Status: PENDING_EXTERNAL_EVIDENCE
> While the consent protocols, task instructions, and survey instruments are fully implemented and ready for execution, in-person testing with live external farm stakeholders has not yet been conducted due to physical harvest scheduling and evaluator availability.
> 
> **Zero-Fabrication Commitment**:
> In accordance with academic and engineering integrity standards, **no fabricated participant responses, false quotes, or artificial Likert averages are presented**.
> 
> The pilot documentation is complete, and the application is prepared to log live participant records as soon as field sessions are administered.
