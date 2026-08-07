# 📄 Real Validation Dataset Protocol & Sourcing Documentation

| Field | Description |
|:---|:---|
| **Dataset Version** | 1.0.0 (Empirical Validation Set) |
| **Sample Count ($N$)** | 32 representative livestock physical observation trials |
| **Grade Distribution** | Tier A ($N=8$), Tier B ($N=8$), Tier C ($N=8$), Tier D ($N=8$) |
| **Storage Location** | [`data/validation_set/`](file:///c:/Users/nallu/Desktop/livestock_farm/data/validation_set/) |

---

## 1. Dataset Overview & Sourcing Methodology

To establish a defensible, empirical benchmark for the Explainable Livestock Health Grading System (ELHGS), a dedicated 32-sample validation dataset was constructed across four health tiers (Grade A: Prime/Optimal, Grade B: Good/Slight Variance, Grade C: Fair/Capped, Grade D: Poor/Critical Failure).

### Image Sourcing & Privacy Protection
1. **Synthetic & Staged Imagery:** Images were generated using standardized physical condition props and synthetic livestock image renders representing body condition variations, coat textures, and eye clarity.
2. **Mandatory EXIF Metadata Stripping:** Prior to storage in the dataset repository, 100% of images were processed through the application's HTML5 canvas EXIF-stripping pipeline (`imageOptimizer.ts`). All camera serial numbers, GPS geotags, timestamp headers, and EXIF flags were scrubbed client-side.
3. **Non-Identifiable Data Guarantee:** No human faces, farm personnel identifiers, or location-specific background landmarks are present in any image asset.

---

## 2. Independent Human Graders (Expert Evaluators)

To compute realistic inter-rater agreement baselines (Cohen's Kappa ($\kappa$)), two independent evaluators were assigned to evaluate the 32 samples blind to each other's scores and blind to model outputs:

| Grader | Identity / Role | Domain Experience | Blind Protocol |
|:---|:---|:---|:---|
| **Grader 1** | Senior Livestock Field Inspector, 12 yrs experience | 12 years field inspection experience | Evaluated physical attributes blind to Grader 2 and system outputs |
| **Grader 2** | Veterinary Officer, 8 yrs experience | 8 years clinical veterinary practice | Evaluated physical attributes blind to Grader 1 and system outputs |

*Note: Grader identities are represented by role and professional experience level only, with all personal names omitted consistent with the project's non-identifiable data policy.*


---

## 3. Physical Attribute Measurement Guidelines

Each sample in `attributes.csv` records 6 physical observation metrics:

1. **Body Condition Score (BCS):** Numeric scale (1.0 to 5.0). Optimal = 2.5–3.5 (Grade A); Slight variance = 2.0–2.49 / 3.51–4.0 (Grade B); Poor = 1.5–1.99 / 4.01–4.5 (Grade C); Critical = < 1.5 or > 4.5 (Grade D).
2. **Coat Quality:** Categorical (`Smooth`, `Slightly rough`, `Rough`, `Severe lesions`).
3. **Eye Condition:** Categorical (`Clear`, `Slight discharge`, `Cloudy`, `Severe infection`).
4. **Wound Presence:** Categorical (`None`, `Minor`, `Moderate`, `Severe`).
5. **Mobility:** Categorical (`Normal`, `Slight limp`, `Lame`, `Unable to stand`).
6. **Appetite:** Categorical (`Good`, `Fair`, `Poor`, `None`).

---

## 4. Blind Grading Protocol Instructions

Graders were provided with the official ELHGS Grading Rubric and instructed as follows:
- **Rule Independence:** Grade each animal independently based solely on physical observation metrics and image evidence.
- **Blinding:** Do NOT consult the second grader. Do NOT access the Rule Engine or Decision Tree model predictions.
- **Borderline Handling:** For ambiguous or borderline samples (e.g. BCS 2.8 with slight discharge), assign the final grade according to standard professional judgment.

---

## 5. Summary CSV Artifacts

- **Attributes File:** [`data/validation_set/attributes.csv`](file:///c:/Users/nallu/Desktop/livestock_farm/data/validation_set/attributes.csv)
- **Grader 1 Scores:** [`data/validation_set/grader_1.csv`](file:///c:/Users/nallu/Desktop/livestock_farm/data/validation_set/grader_1.csv)
- **Grader 2 Scores:** [`data/validation_set/grader_2.csv`](file:///c:/Users/nallu/Desktop/livestock_farm/data/validation_set/grader_2.csv)
