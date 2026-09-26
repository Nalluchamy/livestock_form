# Livestock Health Grading Rubric

> **MANDATORY CLINICAL DISCLAIMER:**
> **ELHGS condition grading is an observational decision-support score, not a veterinary medical diagnosis. Urgent cases require immediate clinical examination by a licensed veterinarian.**
>
> **For full cattle-specific operational standards and visible vs. physical examination taxonomy, see [Cattle Health and Condition Grading Rubric v2.0](cattle_grading_rubric_v2.md).**

This document defines the domain expert rubric for the Explainable Livestock Health Grading System (ELHGS). The Rule Engine uses these criteria to evaluate health attributes and determine the deterministic baseline grade.

## Grading Scale
- **Grade A:** Healthy / Optimal condition; ready for market or breeding.
- **Grade B:** Needs Observation; minor non-acute conditions requiring dietary or husbandry adjustments.
- **Grade C:** Needs Treatment; marked condition deficiencies or localized pathologies requiring clinical intervention.
- **Grade D:** Critical / Urgent; acute distress, severe disease, extreme emaciation, or immobility requiring immediate veterinary attention.

## Evaluation Criteria & Observable Boundaries

> [!CAUTION]
> **STRICT PROTOCOL RULE: NEVER INFER APPETITE OR TEMPORAL MOBILITY SOLELY FROM A 2D PHOTOGRAPH.**
> A static 2D photograph provides zero temporal, behavioural, or kinetic intake data. Physical examination and management records are mandatory for appetite, dynamic locomotion, and live weight.

| Attribute | Category | Grade A (Healthy) | Grade B (Observation) | Grade C (Treatment) | Grade D (Critical) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Body Condition** | Photo-Visible | Optimal (2.5 – 3.5) | Moderate (2.0 – 2.4, 3.6 – 4.0) | Poor (1.5 – 1.9, 4.1 – 4.5) | Emaciated (<1.5) or Morbidly Obese (>4.5) |
| **Coat / Hide** | Photo-Visible | Smooth, clean, shiny | Slightly rough or dull | Rough, minor alopecia | Severe lesions, parasites, mange |
| **Eye Clarity** | Photo-Visible | Clear, bright | Slight discharge | Cloudy, excessive tearing | Severe infection, pinkeye, blindness |
| **Wounds / Injuries** | Photo-Visible | None | Minor scratches | Moderate localized wounds | Severe lacerations, necrotic abscesses |
| **Mobility** | Physical Exam | Normal gait | Slight limp | Lame | Unable to stand (Downer) |
| **Appetite** | Intake Record | Good intake | Fair intake | Poor intake | None / Anorexic |

## Rule Engine Logic
The Rule Engine evaluates the cumulative attributes:
1. **Critical Failure:** If *any* attribute scores a **Grade D**, the overall AI Prediction is automatically **Grade D** and triggers an immediate Urgent Clinical Escalation.
2. **Warning Threshold:** If *two or more* attributes score a **Grade C**, the overall AI Prediction cannot exceed **Grade C**.
3. **Consolidation Average:** If all attributes score **Grade A** or **Grade B**, the overall AI Prediction is the average, favoring the lowest score (e.g., three A's and one B results in a **Grade B**).
