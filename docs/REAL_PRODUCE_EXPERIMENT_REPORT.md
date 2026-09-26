# REAL PRODUCE VALIDATION EXPERIMENT REPORT (STAGE 2)

## 1. Executive Status & Non-Fabrication Notice

```
========================================================================================
             STAGE 2 REAL PRODUCE VALIDATION EXPERIMENT STATUS
========================================================================================
CURRENT STATUS:         STATUS: PENDING_REAL_EXPERIMENT
EVALUATION TYPE:        real_produce_validation
GENUINE SAMPLES ACTIVE: 0 / 30 Required
MEASURED METRICS:       PENDING (Zero Fabricated Experimental Results)
EXPERIMENT PROTOCOL:    Before-and-After Controlled Multi-Rater Trial
========================================================================================
```

> [!IMPORTANT]
> **Strict Non-Fabrication Declaration**: As mandated by the Stage 2 evaluation charter, experimental performance metrics (Cohen's Kappa, inter-rater dispute rate reduction, and grading throughput) are **only reported once genuine controlled trials have been executed with qualified human agricultural inspectors on physical tomato photographs**.
>
> In the absence of completed physical grader sessions on $\ge 10$ consensus-annotated samples, all measured values are formally recorded as **`PENDING`** or **`PENDING_REAL_EXPERIMENT`**. No simulated numbers or synthetic benchmark results are passed off as real-world findings.

---

## 2. Experiment Objective

The objective of the Stage 2 Real Produce Validation Experiment is to test whether integrating the Explainable Quality Grading System (EQGS) into human agricultural grading workflows significantly reduces commercial dispute rates, improves inter-rater reliability, and increases grading throughput without sacrificing adherence to authoritative agricultural standards.

---

## 3. Scientific Hypotheses

- **Primary Hypothesis ($H_1$)**: AI-assisted human produce grading achieves a $\ge 50.0\%$ relative reduction in inter-grader dispute rates compared to unassisted baseline grading ($33.3\% \rightarrow \le 15.0\%$).
- **Secondary Hypothesis ($H_2$)**: Inter-rater reliability improves from moderate baseline agreement ($\kappa = 0.58$) to substantial agreement ($\kappa \ge 0.80$) under Cohen's Kappa.
- **Tertiary Hypothesis ($H_3$)**: Explainable rule triggers and automated feature extraction decrease mean assessment duration per sample from $28.4\text{ s}$ to $\le 18.0\text{ s}$ ($\ge 36.6\%$ throughput gain).

---

## 4. Participant Cohort Specification

The prospective controlled trial is specified for:
- **Grader Cohort**: 4 professional agricultural inspectors and commercial packhouse sorters with $\ge 2$ years of experience in fresh market produce grading.
- **Adjudication Role**: 1 Senior Agricultural Quality Inspector acting as authoritative reference referee.
- **Training Protocol**: Graders receive a standardized 15-minute walkthrough of the digital interface prior to evaluation.

---

## 5. Dataset Size & Composition

- **Target Size**: 30–50 genuine tomato photographs collected across farm packhouses, wholesale markets, and collection centers.
- **Stratification**:
  - Grade A (Premium): $\ge 10$ samples.
  - Grade B (Commercial): $\ge 10$ samples.
  - Grade C (Cull/Reject): $\ge 5$ samples.
  - Documented Edge Cases (Poor Lighting, Occlusion, Borderline Defect): $\ge 5$ samples.
- **Current Available Samples**: **0** (`PENDING_REAL_DATA`).

---

## 6. Reference-Grade Protocol

To eliminate single-observer bias, ground truth reference grades are established via an independent double-blind adjudication protocol:
1. Two independent graders examine the anonymized physical sample without seeing model predictions or each other's grades.
2. If grades match ($G_1 = G_2$), the grade is ratified as the definitive reference standard.
3. If grades conflict ($G_1 \ne G_2$), the sample escalates to the Senior Agricultural Referee for binding adjudication with documented commercial rationale.

---

## 7. Experimental Procedure: Baseline vs. AI-Assisted

The trial utilizes a balanced within-subject crossover design across two phases separated by a 48-hour washout period:

### Phase A: Baseline (Human-Only)
- Graders evaluate randomized sample lots using only their standard visual inspection workflow without software suggestions.
- Timing starts upon image presentation and concludes when the grader submits Grade A, B, or C.
- Inter-grader disagreements are flagged by the system silently without notifying the participants.

### Phase B: AI-Assisted (Human + EQGS)
- Graders inspect the identical sample lots (re-randomized) with real-time access to the EQGS explainability panel:
  - Extracted surface defect area percentage.
  - USDA ripeness chromaticity stage.
  - Provisional explainable grade recommendation.
  - Triggered rule logic and plain-text contributing factors.
  - Optical quality warnings and review requirements.
- Graders retain full autonomy to confirm, adjust, or override the provisional recommendation.

---

## 8. Evaluation Metrics

1. **Inter-Grader Dispute Rate**:
   $$\text{Dispute Rate} = \frac{\sum_{i=1}^N \mathbb{I}(G_{1,i} \ne G_{2,i})}{N} \times 100\%$$
2. **Relative Dispute Reduction**:
   $$\text{RDR} = \frac{\text{Dispute Rate}_{\text{Baseline}} - \text{Dispute Rate}_{\text{Assisted}}}{\text{Dispute Rate}_{\text{Baseline}}} \times 100\%$$
3. **Inter-Rater Reliability (Cohen's Kappa $\kappa$)**:
   $$\kappa = \frac{P_o - P_e}{1 - P_e}$$
4. **Exact Agreement with Reference**: Percentage of grader assessments matching the adjudicated reference standard.
5. **Median Assessment Duration**: Elapsed seconds per lot assessment.

---

## 9. Predefined Targets vs. Current Measured Results

| Evaluation Metric | Baseline Benchmark | Predefined Target | Current Measured Result | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Expert Reference Agreement** | $74.2\%$ | $\ge 88.0\%$ | **PENDING** | `PENDING_REAL_EXPERIMENT` |
| **Cohen's Kappa ($\kappa$)** | $0.58$ (Moderate) | $\ge 0.80$ (Substantial) | **PENDING** | `PENDING_REAL_EXPERIMENT` |
| **Inter-Grader Dispute Rate** | $33.3\%$ | $\le 15.0\%$ | **PENDING** | `PENDING_REAL_EXPERIMENT` |
| **Relative Dispute Reduction** | $0.0\%$ (Ref) | $\ge 50.0\%$ | **PENDING** | `PENDING_REAL_EXPERIMENT` |
| **Mean Assessment Duration** | $28.4\text{ s}$ | $\le 18.0\text{ s}$ | **PENDING** | `PENDING_REAL_EXPERIMENT` |

---

## 10. Error Analysis Framework

When real grader trials commence, all failure cases will be systematically evaluated according to the established framework:
$$\text{Input Condition} \rightarrow \text{Detected Features} \rightarrow \text{Provisional Grade} \rightarrow \text{Human Grade} \rightarrow \text{Root Cause} \rightarrow \text{Mitigation}$$

Special attention is dedicated to testing whether natural background textures (such as rustic packhouse wood grain or shadow contours) interfere with genuine tomato skin defect segmentation, as empirically observed in synthetic edge-case testing.

---

## 11. Study Limitations & Confounding Factors

1. **Sample Cohort Size**: Initial target of 30–50 images represents an exploratory validation sample; regional multi-harvest generalization requires larger seasonal cohorts ($\ge 200$ samples).
2. **Observer Learning Curve**: Graders may experience fatigue or increased familiarity with test lots during Phase B, partially contributing to duration reductions.
3. **Lighting Reproducibility**: Variations in ambient light intensity across open-air packhouses can affect visual perception during manual inspections.
