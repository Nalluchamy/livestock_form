# STAGE 2 MILESTONE DEMONSTRATION SCRIPT & REVIEWER GUIDE
## Explainable Quality Grading System (EQGS) — Fresh-Market Produce & Livestock Health

**Document ID:** EQGS-DOC-STAGE2-DEMO-01  
**Target Milestone:** Stage 2 (70%) Review & Real-World Validation  
**Target Duration:** 15–20 Minutes  
**Target Audience:** Academic Evaluators, Senior Software Architects, Agricultural Domain Experts  
**Demonstration URL / Route:** `/produce` (Guided Demonstration Tab) and `/metrics`

---

## 1. Executive Summary & Session Architecture

This demonstration script provides an end-to-end presentation walkthrough for the Explainable Quality Grading System (EQGS). The primary operational focus is **fresh-market tomato quality grading (Grades A, B, and C)**, with livestock health triage maintained as an active secondary architecture.

### Presentation Timing Budget (Total: 18 Minutes)

| Step | Topic | Target Time | Key Interface View |
| :--- | :--- | :--- | :--- |
| **Step 1** | System Architecture & Component Boundaries | 2:00 min | Architecture Diagram & Technical Stack |
| **Step 2** | Image Ingestion & Optical Quality Gate | 2:30 min | Produce Grading & Diagnostics Tab |
| **Step 3** | Explainable Rule Engine & Diagnostic Panels | 2:30 min | 10-Attribute Analysis & Rule Explanation |
| **Step 4** | Real Produce Dataset Pipeline & Integrity | 2:00 min | Batch Ingestion Tab & Dataset Status |
| **Step 5** | Double-Blind Human Annotation & Escalation | 2:30 min | Double-Blind Annotation Tab |
| **Step 6** | Controlled Before-and-After Trial Runner | 2:30 min | Metrics Dashboard (Produce Experiments) |
| **Step 7** | Real-World Failure Analysis & Edge Cases | 2:00 min | Metrics Dashboard (Failure Analysis Card) |
| **Step 8** | Stakeholder Usability & Field Readiness | 2:00 min | Stakeholder Study Form Tab & Protocol |

---

## 2. Step-by-Step Demonstration Walkthrough

---

### Step 1: System Architecture Overview & Component Boundaries
**Duration:** 2 Minutes  
**On-Screen Action:** Open browser to `/produce` and click on **Step 1: System Architecture** in the *Guided Demonstration* tab.

#### Speaker Script:
> "Good morning, evaluators. Welcome to the Stage 2 demonstration of the Explainable Quality Grading System (EQGS).
>
> Our objective is to bridge computer vision with transparent, auditable decision rules for agricultural quality control. Before diving into live operations, let us review the five architectural layers:
>
> 1. **Client Layer**: A responsive React 18 and TypeScript Progressive Web Application (PWA) with TailwindCSS, offline IndexedDB storage, and client-side optical verification.
> 2. **API & Orchestration Layer**: A high-throughput FastAPI backend enforcing Role-Based Access Control (RBAC) across four tiers: `FARMER`, `EXPERT_GRADER`, `SENIOR_REVIEWER`, and `ADMIN`.
> 3. **Computer Vision & Diagnostic Engine**: OpenCV-based feature extraction measuring 10 morphological and colorimetric attributes, feeding into a deterministic rule engine that eliminates opaque black-box verdicts.
> 4. **Persistence & Data Isolation**: PostgreSQL for relational records, audit logs, and double-blind annotations, strictly isolating genuine produce data (`dataset/produce/real/`) from synthetic development cohorts (`dataset/produce/synthetic/`).
> 5. **Evaluation & Verification Framework**: An automated controlled experiment runner calculating inter-rater reliability (Cohen's Kappa), relative dispute reduction, and grading latency."

#### Visual Cue:
- Highlight the architecture boundaries displayed in the interactive demonstration stepper.

#### Anticipated Reviewer Question:
* **Reviewer**: "How does the system ensure livestock grading and produce grading do not contaminate each other?"
* **Answer**: "The backend maintains separate domain routers (`/api/v1/grading` vs. `/api/v1/produce`), separate database schemas and repositories, and domain-isolated pipelines. The livestock models assess body condition and mobility scoring, whereas produce grading operates on surface defect percentage, color ripeness stages, and circularity."

---

### Step 2: Produce Image Ingestion & Optical Quality Diagnostics
**Duration:** 2 Minutes 30 Seconds  
**On-Screen Action:** Switch to the **🍅 Grading & Diagnostics** tab. Load the sample image `syn_tom_b_001` or upload a sample photograph.

#### Speaker Script:
> "Now, let us examine how images enter the grading pipeline. In farm collection centers, field photographs often suffer from severe blur, extreme backlighting, or severe lens obstruction. Rather than feeding degraded inputs into the grading engine, EQGS implements a strict 12-step ingestion pipeline with an automated **Optical Quality Gate**.
>
> When an image is received:
> 1. **Laplacian Blur Detection**: We calculate the variance of the Laplacian. If sharpness falls below $\tau_{\text{blur}} = 100.0$, the image is halted immediately with an `IMAGE_BLURRED` rejection code.
> 2. **Brightness & Contrast Verification**: We verify mean pixel luminance ($30.0 \le \mu_L \le 235.0$) and dynamic range standard deviation ($\sigma_L \ge 20.0$). Over-exposed or pitch-black photos trigger `LIGHTING_TOO_DARK` or `LIGHTING_OVEREXPOSED`.
> 3. **Geometric & Aspect Ratio Checks**: Resolution must meet minimum dimensions ($256 \times 256$), and aspect ratio must fall between $0.33$ and $3.0$ to eliminate corrupt thumbnails or extreme banner crops.
>
> When quality criteria are satisfied, the pipeline generates SHA-256 integrity hashes, strips sensitive EXIF metadata, creates normalized thumbnails, and produces a calibrated binary mask."

#### Visual Cue:
- Point out the **Image Quality Diagnostic Gate** card showing `Status: VALID (PASS)` with calculated Laplacian variance and luminance metrics.

#### Anticipated Reviewer Question:
* **Reviewer**: "What happens if a farmer uploads an unacceptable photo in the field?"
* **Answer**: "The UI immediately flags the rejection reason—such as 'Image too blurry (variance: 34.2 < 100.0)'—and prompts immediate recapture before the farmer leaves the sorting table, preventing corrupted batches down the line."

---

### Step 3: Explainable Rule Engine & Diagnostic Panels
**Duration:** 2 Minutes 30 Seconds  
**On-Screen Action:** Scroll down on the **🍅 Grading & Diagnostics** tab to inspect the **10-Attribute Analysis Panel** and **Rule-Based Explanation**.

#### Speaker Script:
> "Here lies the core innovation of our system: **Complete Mechanistic Explainability**. Rather than outputting a single probabilistic score from an inscrutable deep neural network, EQGS extracts ten explicit physical attributes:
>
> 1. Surface defect area percentage.
> 2. Defect cluster count.
> 3. Ripeness color stage (Green, Breaker, Turning, Pink, Light Red, Red).
> 4. Mean RGB & HSV channel color distribution.
> 5. Circularity / roundness index ($4\pi \cdot \text{Area} / \text{Perimeter}^2$).
> 6. Major-to-minor axis aspect ratio.
> 7. Effective diameter in normalized pixels.
> 8. Solidity (contour area over convex hull area).
> 9. Skin smoothness and edge roughness standard deviation.
> 10. Stem scar presence and calyx integrity index.
>
> These attributes are evaluated against deterministic standards aligned with USDA and international fresh-market standards:
> - **Grade A (Premium)**: Defect area $< 5.0\%$, circularity $\ge 0.82$, firmness $\ge 0.80$, minimum diameter $\ge 50\text{mm}$.
> - **Grade B (Commercial / Processing)**: Defect area $5.0\% \le \delta < 15.0\%$, circularity $\ge 0.70$.
> - **Grade C (Substandard / Reject)**: Defect area $\ge 15.0\%$, severe surface bruising, or extreme misshape.
>
> The panel shows the exact rule that fired, the threshold condition, and the plain-language justification provided to packhouse workers."

#### Visual Cue:
- Hover over the 10 attribute progress bars and point to the highlighted active rule card.

---

### Step 4: Real Produce Dataset Management & Zero-Fabrication Integrity
**Duration:** 2 Minutes  
**On-Screen Action:** Switch to the **📥 Batch Ingestion** tab and navigate to `/metrics` (Produce Dataset Status card).

#### Speaker Script:
> "A central pillar of Stage 2 is transition toward genuine field validation while maintaining strict academic integrity.
>
> Notice the **Produce Dataset Collection Target**:
> - We have established three balanced collection categories for real-world sampling: **Apparent High-Quality** (10 targets), **Apparent Minor Defects** (10 targets), and **Apparent Substantial Defects** (10 targets).
> - **Crucial Distinction**: These collection categories are merely sampling guidelines for harvesting visual diversity—they are **never** treated as ground truth labels.
>
> In accordance with our **Zero-Fabrication Commitment**:
> - Current Genuine Photographs: **0 / 30**.
> - Genuine Dataset Status: `PENDING_REAL_DATA`.
> - We do not count our 300 photorealistic synthetic images as real data. Synthetic files reside in `dataset/produce/synthetic/`, while genuine field uploads enter `dataset/produce/real/raw/` with a separate CSV manifest.
>
> The Batch Ingestion interface is live, supporting drag-and-drop batch intake, auto-categorization selection, image previews, and per-item quality gate validation."

#### Visual Cue:
- Demonstrate the batch upload file selector and review the zero-count honest indicators on the metrics dashboard.

---

### Step 5: Double-Blind Human Annotation Workflow
**Duration:** 2 Minutes 30 Seconds  
**On-Screen Action:** Switch to the **👥 Double-Blind Annotation** tab on `/produce`.

#### Speaker Script:
> "To establish true ground truth without cognitive anchoring or bias, EQGS provides an enterprise-grade **Double-Blind Annotation Engine**.
>
> Let us walk through the protocol:
> 1. **Blind Isolation**: Grader 1 and Grader 2 evaluate the photograph independently. Neither grader can see the other grader's notes or grade, and critically, the automated AI recommendation is hidden during primary grading.
> 2. **Consensus Ratification**: When Grader 1 and Grader 2 assign the same grade (e.g., both choose Grade A), the system automatically ratifies this consensus as the official ground truth label.
> 3. **Dispute Detection & Escalation**: If Grader 1 assigns Grade A and Grader 2 assigns Grade B, the record is flagged with `DISPUTED` status and escalated to the Senior Reviewer queue.
> 4. **Senior Adjudication**: A Senior Reviewer views both graders' independent submissions, reviews the high-resolution imagery and 10-attribute diagnostics, and renders the binding final verdict with a mandatory audit rationale.
>
> Because real photographs are awaiting harvest collection, our system explicitly displays `PENDING_EXPERT_ANNOTATION` across queues, guaranteeing zero simulated expert grades."

#### Visual Cue:
- Toggle between Grader 1, Grader 2, and Senior Reviewer view modes in the tab.

---

### Step 6: Controlled Before-and-After Trial Runner
**Duration:** 2 Minutes 30 Seconds  
**On-Screen Action:** Navigate to `/metrics` and scroll to **Stage 2 Controlled Experiment: Produce Quality Grading**.

#### Speaker Script:
> "To measure whether our explainable assistant actually improves human performance in packhouses, we built a formal A/B experiment evaluation framework:
>
> - **Cohort A (Baseline Unassisted)**: Human graders grade produce independently without AI assistance.
> - **Cohort B (AI-Assisted with Explanations)**: Human graders receive real-time attribute extractions and explainable rule prompts.
>
> We evaluate five statistical metrics:
> 1. **Inter-Rater Agreement Rate**: Percent of pairs where graders agreed without intervention.
> 2. **Cohen's Kappa ($\kappa$)**: Chance-corrected agreement coefficient.
> 3. **Dispute Rate & Relative Dispute Reduction**: Percentage drop in escalated disagreements:
>    $$\text{RDR} = \frac{\text{Dispute}_{\text{baseline}} - \text{Dispute}_{\text{assisted}}}{\text{Dispute}_{\text{baseline}}}$$
> 4. **Grading Duration**: Median seconds required per specimen.
> 5. **Senior Escalations Count**: Number of cases requiring senior adjudicator intervention.
>
> **Engineering Rigor Note**: If the baseline dispute rate is $0.0\%$, our runner gracefully handles division-by-zero, returning `UNDEFINED` rather than raising a mathematical exception. For real trials, the status correctly indicates `PENDING_REAL_EXPERIMENT` until genuine sample cohorts are processed."

#### Visual Cue:
- Highlight the Controlled Experiment comparison table with sample size counters ($N_{\text{baseline}}$, $N_{\text{assisted}}$) and the baseline vs. assisted columns.

---

### Step 7: Real-World Failure Analysis & Edge Cases
**Duration:** 2 Minutes  
**On-Screen Action:** On `/metrics`, scroll to the **Documented Genuine-Image Edge & Failure Cases** panel.

#### Speaker Script:
> "Computer vision in agriculture often fails at the margins. Rather than claiming 100% laboratory accuracy, we have formalized four real-world failure modes and engineered proactive mitigations:
>
> 1. **Case 1: Severe Motion Blur & Variable Sunlight**
>    - *Failure*: Shaky smartphone capture in open sunlight causes Laplacian score drop and washed-out highlights.
>    - *Mitigation*: The optical quality gate rejects capture immediately; multi-exposure contrast normalization corrects mild glare.
> 2. **Case 2: Partial Occlusion by Foliage, Vine, or Sorting Tray**
>    - *Failure*: Tomato partially hidden by stem or crate wall distorts circularity and area metrics.
>    - *Mitigation*: Solidity analysis detects concave occlusion; the system prompts the operator: 'Rotate specimen to isolate fruit'.
> 3. **Case 3: Borderline Defect Percentage ($4.8\%$ vs $5.2\%$)**
>    - *Failure*: Natural mottling near the $5.0\%$ Grade A/B boundary causes human-machine disagreement.
>    - *Mitigation*: System flags 'Borderline Defect' alert and triggers mandatory double-blind human verification.
> 4. **Case 4: Wooden Packhouse Table & Shadow Artifacts**
>    - *Failure*: Brown wood grain and sharp directional shadows falsely register as skin blemishes.
>    - *Mitigation*: HSV-space color segmentation isolates tomato chroma ($H \in [0, 25] \cup [160, 180]$), discarding table background."

#### Visual Cue:
- Review the 4 interactive cards with severity badges, detection mechanisms, and mitigations.

---

### Step 8: Stakeholder Usability & Field Readiness
**Duration:** 2 Minutes  
**On-Screen Action:** Switch back to `/produce` and click the **📝 Stakeholder Study Form** tab.

#### Speaker Script:
> "Finally, we examine human-centered field readiness. In accordance with `docs/STAKEHOLDER_VALIDATION.md`, we have integrated a full ethical usability evaluation workflow:
>
> 1. **Voluntary Informed Consent**: Explicit ethical safeguards confirming non-punitive evaluation, zero worker surveillance, and anonymized respondent IDs.
> 2. **Structured 5-Task Protocol**:
>    - Task 1: Capture and optical check.
>    - Task 2: Review attribute breakdown and explanation.
>    - Task 3: Double-blind grading submission.
>    - Task 4: Senior adjudication workflow.
>    - Task 5: Offline airplane-mode drafting and local sync.
> 3. **Standardized 5-Item Likert Survey**: Scoring mobile ergonomics, explanation clarity, attribute fidelity, dispute fairness, and remote packhouse viability.
> 4. **Audit Status**: Clearly displayed as `PENDING_EXTERNAL_EVIDENCE` until physical field sessions are administered. The form is fully functional and persists anonymous feedback to our audit trail upon submission.
>
> In conclusion, EQGS delivers a production-grade, fully explainable, mathematically resilient grading platform ready for genuine harvest intake."

#### Visual Cue:
- Walk through the interactive consent checkbox, the 5-task checklist, and the 5-star Likert input controls.

---

## 3. Reviewer FAQ & Defense Guidance

### Q1: "Why hasn't the genuine dataset been collected yet?"
* **Answer**: "Dataset collection requires physical harvesting seasons and farm access. Rather than synthesizing fake data or borrowing uncurated internet images that compromise scientific validity, we engineered the entire ingestion, quality gate, annotation, and trial infrastructure first. The system is 100% prepared to intake, validate, and evaluate the 30 field photos the moment physical collection commences."

### Q2: "How do you prevent graders from colluding during double-blind grading?"
* **Answer**: "The double-blind service enforces session-level isolation. Grader 2's interface does not query or receive Grader 1's record from the backend until both graders have submitted their immutable timestamps. Furthermore, AI recommendations are withheld from graders in baseline mode to prevent anchoring bias."

### Q3: "What makes your rule engine better than an end-to-end convolutional neural network (CNN) or Vision Transformer?"
* **Answer**: "In commercial agricultural sorting, legal and contractual disputes arise over grade rejections. A black-box CNN predicting 'Grade C with 84% probability' provides zero actionable defense to a farmer. Our system provides exact physical metrics: 'Grade C assigned because surface defect is 16.4%, exceeding the 15.0% threshold per Rule R-C-01'. This transforms disputes into objective, verifiable measurements."

### Q4: "How does the system perform offline in rural collection centers?"
* **Answer**: "The PWA uses Service Workers to cache application assets and IndexedDB to queue local image captures and draft annotations. When the device reconnects to Wi-Fi or cellular service, the background sync engine pushes queued records to FastAPI without data loss."

---

## 4. Verification & Sign-Off Checklist for Evaluators

- [x] **Backend Architecture**: FastAPI RESTful services operational with RBAC enforcement.
- [x] **Optical Quality Gate**: Blur, exposure, and aspect ratio rejection verified.
- [x] **Explainable Rule Engine**: 10 attributes extracted with clear USDA-aligned thresholds.
- [x] **Dataset Pipeline**: Real and synthetic produce datasets strictly isolated.
- [x] **Double-Blind Annotation**: Grader isolation, consensus ratification, and senior adjudication active.
- [x] **Controlled Trial Runner**: Statistical comparison framework with Cohen's Kappa and zero-division defense.
- [x] **Failure Case Documentation**: 4 genuine failure modes identified with technical mitigations.
- [x] **Field Usability Protocol**: Ethical consent, 5-task checklist, and 5-point Likert survey ready for external participants.
