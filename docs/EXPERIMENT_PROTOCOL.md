# BEFORE-AND-AFTER CONTROLLED EXPERIMENT PROTOCOL (STAGE 2)

## 1. Study Objective & Hypothesis

The primary objective of the Stage 2 evaluation experiment is to measure the quantitative impact of explainable AI assistance on produce grading consistency, inter-grader dispute rates, and throughput in farm packhouses.

### Formal Experimental Hypotheses
- **$H_1$ (Dispute Reduction)**: Providing graders with real-time explainable rubric feedback and objective computer-vision attributes will reduce the inter-grader dispute rate by at least $30\%$ relative to unassisted human grading.
- **$H_2$ (Inter-Grader Reliability)**: AI assistance will elevate inter-grader agreement (measured by Cohen's kappa $\kappa$) from moderate agreement ($\kappa < 0.65$) to substantial agreement ($\kappa \ge 0.80$).
- **$H_3$ (Assessment Efficiency)**: Graders supported by automated attribute extraction will reduce mean assessment time per sample by at least $20\%$ without compromising grade accuracy against an expert reference.

---

## 2. Experimental Design & Methodology

### 2.1. Counterbalanced Cross-Over Protocol
To prevent memory recall bias (where graders remember grades assigned to specific produce lots during earlier sessions), the study employs a **$2 \times 2$ Counterbalanced Split-Plot Design**:

| Cohort | Session 1 (Block 1: 30 Samples) | Washout Period | Session 2 (Block 2: 30 Samples) |
| :--- | :--- | :--- | :--- |
| **Group 1** (Graders A & B) | **Baseline Condition** (Human-Only, No AI) | 48 Hours | **Assisted Condition** (Explainable AI Active) |
| **Group 2** (Graders C & D) | **Assisted Condition** (Explainable AI Active) | 48 Hours | **Baseline Condition** (Human-Only, No AI) |

- **Sample Set**: 60 authenticated produce samples with pre-established double-blind expert reference grades.
- **Double-Blind Isolation**: In all conditions, Graders submit assessments independently without visibility of other graders' submissions.

---

## 3. Measured Metrics & Mathematical Formulations

### 3.1. Inter-Grader Dispute Rate ($DR$)
A dispute occurs whenever two independent graders assign different grades to the same produce specimen:
$$DR = \frac{\sum_{i=1}^{N} \mathbb{I}(g_{1,i} \ne g_{2,i})}{N} \times 100\%$$
Where:
- $N$ is the number of evaluated samples in the condition.
- $g_{1,i}, g_{2,i} \in \{\text{Grade A}, \text{Grade B}, \text{Grade C}\}$ are the independent grades.

### 3.2. Relative Dispute-Rate Reduction ($RDR$)
$$RDR = \frac{DR_{\text{Baseline}} - DR_{\text{Assisted}}}{DR_{\text{Baseline}}} \times 100\%$$

### 3.3. Cohen's Kappa ($\kappa$)
Measures inter-rater agreement above chance:
$$\kappa = \frac{P_o - P_e}{1 - P_e}$$
Where $P_o$ is observed agreement proportion and $P_e$ is hypothetical chance agreement proportion.

### 3.4. Agreement with Expert Reference ($Acc_{\text{ref}}$)
$$Acc_{\text{ref}} = \frac{1}{2N} \sum_{i=1}^{N} \left[ \mathbb{I}(g_{1,i} = g_{\text{ref},i}) + \mathbb{I}(g_{2,i} = g_{\text{ref},i}) \right] \times 100\%$$

### 3.5. Mean Assessment Time ($T_{\text{avg}}$)
$$T_{\text{avg}} = \frac{1}{N} \sum_{i=1}^{N} (t_{\text{submission}, i} - t_{\text{image\_view}, i})$$
Recorded in seconds using client-side precision timers.

---

## 4. Predefined Targets vs. Baseline Benchmark

| Metric | Historical / Baseline | Predefined Target | Real Measured Value |
| :--- | :--- | :--- | :--- |
| **Dispute Rate ($DR$)** | $33.3\%$ | $\le 15.0\%$ | *Stored in PostgreSQL* / `PENDING` |
| **Relative Dispute Reduction ($RDR$)** | Baseline Reference ($0\%$) | $\ge 50.0\%$ reduction | *Stored in PostgreSQL* / `PENDING` |
| **Cohen's Kappa ($\kappa$)** | $0.58$ (Moderate) | $\ge 0.80$ (Substantial) | *Stored in PostgreSQL* / `PENDING` |
| **Expert Reference Agreement** | $74.2\%$ | $\ge 88.0\%$ | *Stored in PostgreSQL* / `PENDING` |
| **Mean Assessment Time** | $28.4\text{ s}$ | $\le 18.0\text{ s}$ | *Stored in PostgreSQL* / `PENDING` |

---

## 5. PostgreSQL Persistence Schema

Experiment executions are permanently stored in the `experiment_results` table:
- `experiment_id`: UUID primary key.
- `experiment_name`: String identifier (e.g., `EXP_STAGE2_PRODUCE_ASSISTED_001`).
- `dataset_version`: String hash of dataset split.
- `sample_count`: Integer sample count.
- `condition`: String (`HUMAN_ONLY` or `AI_ASSISTED`).
- `metrics_payload`: JSONB containing inter-grader agreement, dispute count, kappa, mean duration, and F1 scores.
- `is_synthetic`: Boolean flag (strictly `FALSE` for genuine field trials).
- `created_at`: Timestamp.

---

## 6. Execution Status & Non-Fabrication Policy

> [!NOTE] Experiment Execution Status
> When formal live trials with external produce graders have not yet been completed, the application reports:
> `PENDING_EXPERIMENT`
>
> The experiment runner engine (`backend/evaluation/produce_experiment_runner.py`) provides the end-to-end mathematical calculation, trial simulation verification for tests, and PostgreSQL persistence pipeline. Live production displays reflect only genuine trial records.
