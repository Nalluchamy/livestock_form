# Explainable Grading Rules Engine

The Explainable Livestock Health Grading System (ELHGS) employs a deterministic Rule Engine in Phase 3 to establish a robust baseline of explainability before introducing Machine Learning.

## Grading Rubric
The engine evaluates attributes based on the following scale:
- **Grade A:** Healthy
- **Grade B:** Needs Observation
- **Grade C:** Needs Treatment
- **Grade D:** Critical

| Attribute | A | B | C | D |
| :--- | :--- | :--- | :--- | :--- |
| **Body Condition** | 2.5 - 3.5 | 2.0 - 2.4, 3.6 - 4.0 | 1.5 - 1.9, 4.1 - 4.5 | < 1.5 or > 4.5 |
| **Coat Quality** | Smooth | Slightly rough | Rough | Severe lesions |
| **Eye Condition**| Clear | Slight discharge | Cloudy | Severe infection |
| **Wound Presence**| None | Minor | Moderate | Severe |
| **Mobility** | Normal | Slight limp | Lame | Unable to stand |
| **Appetite** | Good | Fair | Poor | None |

## Rule Priority
The rules are evaluated in the following hierarchical priority:
1. **Critical Failure Rule:** If *any* attribute evaluates to a Grade D, the overall system prediction is immediately forced to Grade D.
2. **Warning Threshold Rule:** If *two or more* attributes evaluate to Grade C, the overall system prediction is capped at a maximum of Grade C.
3. **Average Consolidation:** If the above rules do not trigger, the system averages the numeric equivalents of the grades (A=1, B=2, C=3, D=4) and rounds to determine the final grade.

## Confidence Calculation
Confidence starts at `100%` and is penalized deterministically:
- `-15%` for every missing attribute.
- `-20%` if no image is associated with the grading event.
- `-20%` if there are contradictory observations (e.g., an 'A' grade attribute mixed with a 'D' grade attribute).

If confidence drops below `50%`, the system automatically recommends a human review.

## Disagreement Workflow
The system actively detects disagreements between human input and AI logic:
1. Human Grader inputs attributes and submits their manual grade (e.g., `B`).
2. The System runs the rules and outputs its grade (e.g., `C`).
3. The System detects the mismatch.
4. The System **never** overwrites the human grade. Instead, it generates a `Disagreement` object and flags the record for Senior Review.

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
  "review_required": false
}
```
