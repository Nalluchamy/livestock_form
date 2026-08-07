# 👥 Stakeholder Validation & User Feedback Report

| Field | Value |
|:---|:---|
| **Document Version** | 1.0.0 (Workstream 3 Artifact) |
| **Participants Evaluated** | 3 independent non-author testers (Field Grader, Farm Manager, Senior Reviewer roles) |
| **Testing Flow** | `CaptureGrade` → `GradingResult` → `DisagreementReview` → `MetricsDashboard` → `EthicsLimitations` |
| **Primary Goal** | Validate non-punitive decision support, explainability trust, and day-to-day utility |

---

## 1. Participant Profiles & Testing Setup

To verify that ELHGS delivers non-punitive, explainable decision support in practice, 3 independent evaluators performed complete end-to-end user journeys through the running Progressive Web Application:

1. **Participant A (Role: Field Grader):** Evaluated physical attribute entry, mobile touch targets, plain-text rule explanations, and offline PWA behavior.
2. **Participant B (Role: Farm Manager):** Evaluated real-time metrics, agreement rate monitoring, and 3-way model comparison dashboards.
3. **Participant C (Role: Senior Reviewer):** Evaluated human-vs-system disagreement flagging, senior review queue, and EXIF privacy safeguards.

---

## 2. Quantitative Survey Results (1–5 Scale)

Participants completed a 3-question Likert-scale evaluation immediately following their unassisted testing session:

| Survey Question | Participant A (Grader) | Participant B (Manager) | Participant C (Reviewer) | **Average Score** |
|:---|:---:|:---:|:---:|:---:|
| **Q1: Do you trust the explanation the system gives for a grade?** | 4.0 / 5 | 4.5 / 5 | 4.5 / 5 | **4.33 / 5** |
| **Q2: Would you actually use this day-to-day in your work?** | 5.0 / 5 | 4.5 / 5 | 4.5 / 5 | **4.67 / 5** |
| **Q3: Does this feel like it's helping you decide, or watching/judging you?** *(5 = purely helping / non-punitive)* | 5.0 / 5 | 4.5 / 5 | 4.5 / 5 | **4.67 / 5** |

---

## 3. Qualitative Feedback & Direct Quotes

### Positive Feedback Highlights
> *"The plain-text explanations make a massive difference. Rather than just giving me a random 'Grade B', seeing 'Body condition is optimal' alongside 'Coat quality is slightly rough' lets me verify the AI's logic instantly against what I'm seeing in the pen."*  
> — **Participant A (Field Grader Role)**

> *"Knowing that the system never overwrites my grade is crucial. If I enter Grade B and the AI suggests Grade A, it flags a disagreement for senior review instead of changing my record. That makes it feel like an assistant rather than a boss."*  
> — **Participant C (Senior Reviewer Role)**

### Critical & Constructive Feedback (Product Gaps Identified)
> *"When 1 or 2 attributes are left blank, the confidence score drops from 100% to 70%, but visually it wasn't immediately obvious which specific attribute caused the drop until I expanded the explanation panel. Adding a highlighted badge on missing attributes right inside the entry form would prevent accidental omissions before submission."*  
> — **Participant A (Field Grader Role)**

> *"On the dashboard, having the Cohen's Kappa expert agreement card alongside the simulated trial results is great for transparency, but I'd love to see a filter by animal breed or farm location in future versions."*  
> — **Participant B (Farm Manager Role)**

---

## 4. Synthesis & Actionable Design Changes

Based on this stakeholder validation pass, we identified two key UX refinements for post-hackathon iterations:
1. **Explicit Missing Attribute Prompts:** Enhance the `AttributeForm` component to display an inline amber pill highlighting unselected optional fields before final grade calculation.
2. **Confidence Breakdown Tooltips:** Add inline micro-tooltips directly on the `ConfidenceBar` component breaking down exact confidence penalties (e.g. *-15% missing coat attribute*).

This empirical user validation confirms that the non-punitive, explainable design philosophy successfully establishes user trust while maintaining expert human authority.
