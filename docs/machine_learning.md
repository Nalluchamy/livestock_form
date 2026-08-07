# Machine Learning & Explainable AI (XAI) Documentation

Phase 6 introduces an explainable Machine Learning (ML) advisory layer to the Explainable Livestock Health Grading System (ELHGS). This layer operates alongside the Phase 3 Rule Engine to provide probabilistic predictions, feature importance rankings, and multi-model consensus evaluations without overriding human decision-making.

## Core Principles
1. **Rule Engine Baseline:** The Rule Engine remains the primary official logic. The ML layer serves as an advisory recommendation tool.
2. **Human Supremacy:** Neither the Rule Engine nor the ML models ever overwrite human expert decisions.
3. **No Black Boxes:** Only white-box/glass-box algorithms (Decision Trees and Linear Classifiers) are deployed to ensure feature attribution and decision path transparency.

---

## Dataset & Features

The ML pipeline is trained on structured, non-PII, EXIF-stripped physical observations:

| Feature Name | Type | Scaling / Encoding | Description |
| :--- | :--- | :--- | :--- |
| `body_condition` | Float (1.0 - 5.0) | Numerical Raw | 1=Emaciated, 3=Optimal, 5=Obese |
| `coat_quality` | Ordinal | 0=Smooth -> 3=Severe lesions | Physical hide/coat state |
| `eye_condition` | Ordinal | 0=Clear -> 3=Severe infection | Ocular health score |
| `wound_presence` | Ordinal | 0=None -> 3=Severe | Injury severity score |
| `mobility` | Ordinal | 0=Normal -> 3=Unable to stand | Gait & movement capability |
| `appetite` | Ordinal | 0=Good -> 3=None | Feeding behavior |

---

## Algorithms & Explainability Mechanics

### 1. Decision Tree Classifier
- **Parameters:** `max_depth=5`, `random_state=42`
- **Explainability:** Feature importances are extracted directly from node impurity reductions. Top decision paths reveal which physical attributes triggered class splits.

### 2. Logistic Regression
- **Parameters:** `max_iter=1000`, `random_state=42`, `multi_class='auto'`
- **Explainability:** Model coefficients ($\beta_i$) represent positive/negative weights for each grade class (A, B, C, D).

---

## Benchmark & 3-Way Comparison Results

Evaluated on 600 synthetic livestock health observations:

| Model / Baseline | Accuracy | Precision | Recall | F1-Score | Avg Time / Sample |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Rule Engine (Baseline)** | 64.67% | 76.54% | 64.67% | 66.89% | 0.045 ms |
| **Decision Tree** | **88.17%** | **88.94%** | **88.17%** | **88.22%** | **0.004 ms** |
| **Logistic Regression** | 67.83% | 70.12% | 67.83% | 68.32% | 0.008 ms |

### Key Takeaway
The **Decision Tree Classifier** achieved the highest accuracy (88.17% [measured, 600 synthetic samples]), capturing non-linear interactions between attributes (e.g., severe wound + low BCS -> forced Grade D) while remaining completely transparent. Disagreements between the Rule Engine and the Decision Tree occur in ~34% of borderline cases, perfectly feeding into our Senior Review Queue.

> **Real Validation Update:** On the N=32 real validation dataset, the Rule Engine (κ=0.63, 71.9% match) outperforms the Decision Tree ML (κ=0.30, 53.1% match) due to a synthetic training heuristic distribution mismatch. See docs/dataset_protocol.md for details.

---

## Prediction Output Format

```json
{
  "model": "Decision Tree Classifier",
  "grade": "B",
  "confidence": 91.2,
  "top_features": [
    "Wound presence",
    "Body condition",
    "Mobility"
  ],
  "explanations": [
    "Wound presence contributed 42.1% to decision tree split.",
    "Body condition contributed 28.5% to decision tree split."
  ],
  "prediction_time_ms": 0.45
}
```
