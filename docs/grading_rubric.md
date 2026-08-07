# Livestock Health Grading Rubric

This document serves as the simulated domain expert rubric for the Explainable Livestock Health Grading System (ELHGS) hackathon project. The Rule Engine (Phase 3) will use these exact criteria to evaluate the `dim_criterion` data and determine the deterministic baseline grade.

## Grading Scale
- **Grade A:** Excellent health; ready for market/breeding.
- **Grade B:** Good health; minor issues that do not immediately impact value.
- **Grade C:** Fair health; requires monitoring or mild intervention.
- **Grade D:** Poor health; requires immediate veterinary attention; not fit for market.

## Evaluation Criteria

| Attribute | Grade A (Excellent) | Grade B (Good) | Grade C (Fair) | Grade D (Poor) |
| :--- | :--- | :--- | :--- | :--- |
| **Body Condition** | Good (optimal fat/muscle ratio) | Moderate (slightly under/overweight) | Poor (visible ribs or excessive fat) | Emaciated (severe malnutrition) |
| **Coat / Hide** | Smooth, clean, shiny | Slightly rough or dull | Rough, minor hair loss | Severe lesions, parasites, or mange |
| **Wounds / Injuries** | None | Minor scratches | Moderate, localized wounds | Severe, infected, or lameness |
| **Eye Clarity** | Clear, bright | Slight discharge | Cloudy, excessive tearing | Severe infection, blindness |
| **Respiration** | Normal, unlabored | Slightly elevated | Noticeably labored or coughing | Severe distress, persistent coughing |

## Rule Engine Logic (Draft)
The Rule Engine will evaluate the cumulative attributes:
1. **Critical Failure:** If *any* attribute scores a **Grade D**, the overall AI Prediction is automatically **Grade D**.
2. **Warning Threshold:** If *two or more* attributes score a **Grade C**, the overall AI Prediction cannot exceed **Grade C**.
3. **Good Standing:** If all attributes score **Grade A** or **Grade B**, the overall AI Prediction is the average, favoring the lowest score (e.g., three A's and one B results in a **Grade B**).

> [!NOTE]
> This rubric simulates real-world veterinary criteria and provides the deterministic foundation necessary to generate the `explanation` strings required by our ethical and explainability guidelines.
