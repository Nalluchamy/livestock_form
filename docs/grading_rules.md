# Explainable Grading Rules Engine

> **MANDATORY CLINICAL DISCLAIMER:**
> **ELHGS condition grading is an observational decision-support score, not a veterinary medical diagnosis. Urgent cases require immediate clinical examination by a licensed veterinarian.**
>
> **For full cattle-specific operational standards and visible vs. physical examination taxonomy, see [Cattle Health and Condition Grading Rubric v2.0](cattle_grading_rubric_v2.md).**

The Explainable Livestock Health Grading System (ELHGS) employs a deterministic Rule Engine to establish a robust baseline of explainability before introducing Machine Learning.

## Grading Rubric
The engine evaluates attributes based on the following scale:
- **Grade A:** Healthy
- **Grade B:** Needs Observation
- **Grade C:** Needs Treatment
- **Grade D:** Critical

> [!CAUTION]
> **STRICT PROTOCOL RULE: NEVER INFER APPETITE OR TEMPORAL MOBILITY SOLELY FROM A 2D PHOTOGRAPH.**
> A single static photograph cannot capture metabolic appetite or dynamic kinetic gait. These values must come from direct management logs or dynamic clinical examinations.

| Attribute | Acquisition Type | A | B | C | D |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Body Condition** | Photo-Visible | 2.5 - 3.5 | 2.0 - 2.4, 3.6 - 4.0 | 1.5 - 1.9, 4.1 - 4.5 | < 1.5 or > 4.5 |
| **Coat Quality** | Photo-Visible | Smooth | Slightly rough | Rough | Severe lesions |
| **Eye Condition**| Photo-Visible | Clear | Slight discharge | Cloudy | Severe infection |
| **Wound Presence**| Photo-Visible | None | Minor | Moderate | Severe |
| **Mobility** | Clinical Exam | Normal | Slight limp | Lame | Unable to stand |
| **Appetite** | Intake Log | Good | Fair | Poor | None |

## Rule Priority
The rules are evaluated in the following hierarchical priority:
1. **Critical Failure Rule:** If *any* attribute evaluates to a Grade D, the overall system prediction is immediately forced to Grade D, and an urgent veterinary escalation alert is triggered.
2. **Warning Threshold Rule:** If *two or more* attributes evaluate to Grade C, the overall system prediction is capped at a maximum of Grade C.
3. **Average Consolidation:** If the above rules do not trigger, the system averages the numeric equivalents of the grades (A=1, B=2, C=3, D=4) and rounds to determine the final grade.

## Confidence Calculation
Confidence starts at `100%` and is penalized deterministically:
- `-15%` for every missing attribute.
- `-20%` if no image is associated with the grading event.
- `-20%` if there are contradictory observations (e.g., an 'A' grade attribute mixed with a 'D' grade attribute).

If confidence drops below `50%`, the system automatically recommends a human review.

## Urgent Clinical Escalation
Urgent escalation is triggered when:
- System prediction or expert input assigns **Grade D**.
- **Wound Presence** is `Severe`.
- **Mobility** is `Unable to stand`.
- **Body Condition** is $<1.5$ (severe emaciation) or $>4.5$ (extreme obesity).
- **Eye Condition** is `Severe infection`.

## Disagreement Workflow
The system actively detects disagreements between human input and AI logic:
1. Human Grader inputs attributes and submits their manual grade (e.g., `B`).
2. The System runs the rules and outputs its grade (e.g., `C`).
3. The System detects the mismatch.
4. The System **never** overwrites the human grade. Instead, it generates a `DisagreementReview` record and flags it for Senior Review.

## Explanation Format
Explanations are generated natively by tracing the fired rules:

```json
{
  "grade": "D",
  "confidence": 85.0,
  "reasons": [
    "Critical Failure: Wound presence is severe"
  ],
  "missing_attributes": ["appetite"],
  "review_required": false,
  "urgent_escalation": true,
  "escalation_reasons": ["Wound presence is severe"],
  "clinical_disclaimer": "Condition grade is an observational decision-support score, not a veterinary medical diagnosis. Urgent cases require immediate clinical examination."
}
```
