# Product Requirements Document (PRD)

## Explainable Livestock Health Grading System (ELHGS)

| Field | Value |
|:---|:---|
| **Document Version** | 1.0.0 |
| **Status** | Final — Approved for Hackathon Submission |
| **Last Updated** | August 6, 2026 |
| **Product Owner** | Team ELHGS |

---

## Table of Contents

1. [Executive Overview](#1-executive-overview)
2. [Problem Statement](#2-problem-statement)
3. [Goals & Success Metrics](#3-goals--success-metrics)
4. [Target Users & Personas](#4-target-users--personas)
5. [User Stories & Acceptance Criteria](#5-user-stories--acceptance-criteria)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [System Architecture](#8-system-architecture)
9. [Data Model](#9-data-model)
10. [API Specification](#10-api-specification)
11. [Rule Engine Specification](#11-rule-engine-specification)
12. [Machine Learning Specification](#12-machine-learning-specification)
13. [Offline & Sync Specification](#13-offline--sync-specification)
14. [Security & Privacy Requirements](#14-security--privacy-requirements)
15. [UI/UX Requirements](#15-uiux-requirements)
16. [Deployment & Infrastructure](#16-deployment--infrastructure)
17. [Testing Strategy](#17-testing-strategy)
18. [Risks & Mitigations](#18-risks--mitigations)
19. [Release Plan](#19-release-plan)
20. [Appendices](#20-appendices)

---

## 1. Executive Overview

### 1.1 Product Vision

ELHGS is an **AI-assisted decision-support system** that reduces valuation disputes between livestock health graders by providing transparent, explainable grading decisions. The system supports human decision-making — it **MUST NEVER replace expert reviewers**.

### 1.2 Value Proposition

| Stakeholder | Pain Point | ELHGS Value |
|:---|:---|:---|
| **Field Graders** | Subjective interpretation leads to inconsistent grades | Instant Rule Engine + ML advisory with plain-text reasons |
| **Farm Managers** | Up to 35% dispute rate causes financial loss | 71.8% measured dispute reduction |
| **Veterinarians** | Black-box AI models are rejected and untrusted | White-box Decision Tree with exact feature importance |
| **Buyers** | Slow evaluation process delays market transactions | 67.3% evaluation time reduction (5.2 min → 1.7 min) |
| **Regulatory Bodies** | Lack of audit trail for grading decisions | Full Star Schema audit history with timestamped events |

### 1.3 Core Design Principles

1. **Explainability Over Accuracy:** Every AI recommendation includes plain-text reasoning understandable by non-technical stakeholders.
2. **Human Authority Is Absolute:** The system never overrides, auto-corrects, or alters a human grader's final decision.
3. **Offline-First Architecture:** Field workers must be able to grade livestock with zero internet connectivity.
4. **Privacy by Design:** No surveillance capability. All camera EXIF metadata is stripped client-side before transmission.
5. **Deterministic Baseline:** The Rule Engine provides a repeatable, auditable baseline independent of ML model behavior.

---

## 2. Problem Statement

### 2.1 Current State

Livestock health grading in agricultural markets relies on individual human perception. When two field graders independently assess the same animal, their grades frequently disagree due to:

- **Subjective interpretation** of physical attributes (body condition, coat, eyes, wounds).
- **Inconsistent application** of grading rubrics across regions and individuals.
- **No decision audit trail** — grades are recorded without reasoning or evidence.
- **No technological support** in remote pastures lacking cellular connectivity.

### 2.2 Measured Impact

- **Dispute Rate:** Up to 35% of livestock valuations result in buyer-seller disagreements.
- **Financial Loss:** Inconsistent grading directly affects livestock sale prices, insurance claims, and breeding valuations.
- **Time Cost:** Manual evaluation averages 5.2 minutes per animal, with disputes adding additional review cycles.

### 2.3 Why Existing Solutions Fail

| Approach | Failure Mode |
|:---|:---|
| Pure manual grading | Slow, subjective, no audit trail |
| Black-box deep learning (CNN/ResNet) | Rejected by veterinarians — no explainability |
| Cloud-only AI services | Unusable in remote pastures without internet |
| Simple threshold calculators | No learning capability, no confidence scoring |

---

## 3. Goals & Success Metrics

### 3.1 Primary Goals

| # | Goal | Measurement |
|:---:|:---|:---|
| G1 | Reduce inter-grader dispute rate | ≥ 50% reduction in controlled trials |
| G2 | Reduce per-animal evaluation time | ≥ 40% time reduction |
| G3 | Provide transparent explanations for every grade | 100% of grades include plain-text reasons |
| G4 | Preserve human authority on 100% of decisions | System never auto-modifies human grades |
| G5 | Enable offline grading in remote locations | Full functionality with zero connectivity |

### 3.2 Achieved Results

> *Note: Results obtained from a simulated evaluation framework using 200 representative grading trials based on the project's synthetic dataset and grading rubric.*

| Metric | Target | Achieved |
|:---|:---:|:---:|
| Dispute Reduction | ≥ 50% | **71.8%** ✅ |
| Time Savings | ≥ 40% | **67.3%** ✅ |
| Explanation Coverage | 100% | **100%** ✅ |
| Human Authority Preservation | 100% | **100%** ✅ |
| Offline Grading | Full | **Full** ✅ |

### 3.3 Key Performance Indicators (KPIs)

- **Agreement Rate:** Percentage of evaluations where human and system grades align.
- **Average Confidence Score:** Mean system confidence across all grading events.
- **Pending Senior Reviews:** Count of flagged disagreements awaiting resolution.
- **Low-Confidence Cases:** Count of evaluations with confidence < 50%.
- **Sync Success Rate:** Percentage of offline-queued events successfully synchronized.

---

## 4. Target Users & Personas

### Persona 1: Field Grader (Primary User)

| Attribute | Description |
|:---|:---|
| **Role** | Livestock health field inspector |
| **Technical Skill** | Low to moderate — comfortable with mobile apps |
| **Environment** | Remote pastures, often with limited or no internet |
| **Pain Points** | Needs quick grading; fears being replaced by AI; wants to understand system logic |
| **Key Need** | Instant grade with clear explanation; works offline |

### Persona 2: Farm Manager (Dashboard User)

| Attribute | Description |
|:---|:---|
| **Role** | Farm operations manager |
| **Technical Skill** | Moderate — uses web dashboards regularly |
| **Environment** | Office with stable internet |
| **Pain Points** | Needs herd-level health trends; must identify dispute patterns |
| **Key Need** | Real-time metrics dashboard; historical grading analytics |

### Persona 3: Senior Reviewer (Dispute Resolver)

| Attribute | Description |
|:---|:---|
| **Role** | Veterinarian or senior grading authority |
| **Technical Skill** | High — understands medical and statistical terminology |
| **Environment** | Office or mobile |
| **Pain Points** | Needs to audit flagged disagreements with full context |
| **Key Need** | Disagreement queue with side-by-side human vs. system comparison |

### Persona 4: Regulatory Auditor (Compliance User)

| Attribute | Description |
|:---|:---|
| **Role** | Agricultural standards compliance inspector |
| **Technical Skill** | Moderate |
| **Environment** | Office |
| **Pain Points** | Needs verifiable, tamper-evident grading audit trails |
| **Key Need** | Timestamped event history with linked evidence and explanations |

---

## 5. User Stories & Acceptance Criteria

### US-01: Submit a Livestock Health Grade

**As a** Field Grader,  
**I want to** input physical observation attributes and receive an instant health grade,  
**so that** I can make a consistent, informed grading decision.

**Acceptance Criteria:**
- [ ] User can input: Body Condition Score (1.0–5.0), Coat Quality, Eye Condition, Wound Presence, Mobility, Appetite.
- [ ] System returns a Grade (A/B/C/D), Confidence Score (0–100%), and plain-text explanation within 1 second.
- [ ] Grade is persisted to the database as a `FactGradingEvent`.
- [ ] If Demo Mode is ON, sample and grader records are auto-provisioned.

### US-02: View Explainable Reasoning

**As a** Field Grader,  
**I want to** see exactly why the system recommended a particular grade,  
**so that** I can trust the recommendation and identify potential errors.

**Acceptance Criteria:**
- [ ] Each attribute shows its individual sub-grade (A/B/C/D) and reason.
- [ ] If a Critical Failure Rule was triggered, it is explicitly stated.
- [ ] If a Warning Threshold Rule was triggered, it is explicitly stated.
- [ ] The final grade calculation logic is shown as a step-by-step explanation.

### US-03: Record Human Disagreement

**As a** Field Grader,  
**I want to** submit my own grade even if it differs from the system recommendation,  
**so that** my expert judgment is preserved and the disagreement is flagged for review.

**Acceptance Criteria:**
- [ ] System NEVER auto-overwrites the human grade.
- [ ] If human grade ≠ system grade, a `Disagreement` record is created.
- [ ] Disagreement is marked as `review_required = true`.
- [ ] Senior Reviewer can see the disagreement in the review queue.

### US-04: Grade Livestock Offline

**As a** Field Grader working in a remote pasture,  
**I want to** grade livestock without internet connectivity,  
**so that** I am not blocked by network availability.

**Acceptance Criteria:**
- [ ] PWA installs on device and works offline after first load.
- [ ] Grading events save to IndexedDB (`ELHGS_Offline_DB`) when offline.
- [ ] Visual indicator shows current online/offline status.
- [ ] When connectivity is restored, queued events auto-sync via `POST /api/v1/sync`.

### US-05: Review Disagreements

**As a** Senior Reviewer,  
**I want to** see all flagged disagreements between human and system grades,  
**so that** I can audit decisions and resolve disputes.

**Acceptance Criteria:**
- [ ] Disagreement queue shows: human grade, system grade, confidence, timestamp.
- [ ] Reviewer can approve or override the flagged event.
- [ ] Resolution is recorded with timestamp and reviewer identity.

### US-06: Monitor Herd Health Metrics

**As a** Farm Manager,  
**I want to** see real-time dashboard metrics for grading activity,  
**so that** I can identify trends, outliers, and dispute patterns.

**Acceptance Criteria:**
- [ ] Dashboard displays: Total Gradings, Agreement Rate, Disagreement Rate, Average Confidence.
- [ ] Dashboard shows Pending Reviews and Low-Confidence Cases counts.
- [ ] Dashboard includes 3-way model comparison (Rule Engine vs. Decision Tree vs. Logistic Regression).

### US-07: Protect Worker Privacy

**As a** Farm Worker being photographed during grading,  
**I want** my location and camera metadata automatically stripped,  
**so that** I am protected from surveillance.

**Acceptance Criteria:**
- [ ] When an image is selected in the upload component, EXIF metadata (GPS, camera serial, timestamps) is stripped client-side via HTML5 canvas redraw.
- [ ] No raw EXIF data is ever transmitted to the backend.
- [ ] `exif_stripped` flag is set to `true` in the `dim_image` record.

---

## 6. Functional Requirements

### FR-01: Rule Engine Grading Pipeline

| ID | Requirement | Priority |
|:---|:---|:---:|
| FR-01.1 | System SHALL evaluate 6 physical attributes: `body_condition` (1.0–5.0), `coat_quality`, `eye_condition`, `wound_presence`, `mobility`, `appetite`. | P0 |
| FR-01.2 | System SHALL map each attribute to a sub-grade (A/B/C/D) using the defined rubric. | P0 |
| FR-01.3 | System SHALL apply Critical Failure Rule: Any Grade D attribute → Final Grade D. | P0 |
| FR-01.4 | System SHALL apply Warning Threshold Rule: ≥ 2 Grade C attributes → Maximum Grade C. | P0 |
| FR-01.5 | System SHALL calculate average grade from sub-grades when no override rules apply. | P0 |
| FR-01.6 | System SHALL generate plain-text reasons for each sub-grade and the final grade. | P0 |

### FR-02: Confidence Scoring

| ID | Requirement | Priority |
|:---|:---|:---:|
| FR-02.1 | Base confidence SHALL start at 100%. | P0 |
| FR-02.2 | Each missing attribute SHALL reduce confidence by 15%. | P0 |
| FR-02.3 | Absence of an associated image SHALL reduce confidence by 20%. | P0 |
| FR-02.4 | Contradicting observations (e.g., Grade A + Grade D) SHALL reduce confidence by 20%. | P0 |
| FR-02.5 | If confidence < 50%, the evaluation SHALL be automatically flagged for Senior Review. | P0 |

### FR-03: Disagreement Detection & Human-in-the-Loop

| ID | Requirement | Priority |
|:---|:---|:---:|
| FR-03.1 | If human grade ≠ system grade, system SHALL create a Disagreement record. | P0 |
| FR-03.2 | System SHALL NEVER auto-modify, overwrite, or replace the human grade. | P0 |
| FR-03.3 | Disagreement record SHALL include: human grade, system grade, reason, review_required flag. | P0 |

### FR-04: Machine Learning Advisory Layer

| ID | Requirement | Priority |
|:---|:---|:---:|
| FR-04.1 | System SHALL train and deploy a Decision Tree Classifier as the primary ML model. | P1 |
| FR-04.2 | System SHALL train and deploy a Logistic Regression model for comparison benchmarking. | P1 |
| FR-04.3 | ML predictions SHALL include feature importance percentages. | P1 |
| FR-04.4 | ML predictions SHALL NOT replace or override Rule Engine grades. | P0 |
| FR-04.5 | If ML grade ≠ Rule Engine grade, the disagreement SHALL be flagged. | P1 |

### FR-05: Offline PWA & Synchronization

| ID | Requirement | Priority |
|:---|:---|:---:|
| FR-05.1 | Application SHALL install as a Progressive Web App on supported browsers. | P0 |
| FR-05.2 | Grading events SHALL be stored in IndexedDB when offline. | P0 |
| FR-05.3 | Two-stage sync SHALL upload attribute JSON first, then compressed images. | P1 |
| FR-05.4 | Sync SHALL automatically trigger when network connectivity is restored. | P0 |

### FR-06: Metrics Dashboard

| ID | Requirement | Priority |
|:---|:---|:---:|
| FR-06.1 | Dashboard SHALL display: Total Gradings, Agreement Rate, Disagreement Rate, Average Confidence. | P0 |
| FR-06.2 | Dashboard SHALL display Pending Reviews and Low-Confidence Cases. | P0 |
| FR-06.3 | Dashboard SHALL include 3-way model comparison visualization. | P1 |

### FR-07: Grading History & Audit Trail

| ID | Requirement | Priority |
|:---|:---|:---:|
| FR-07.1 | System SHALL persist every grading event with timestamp, grade, confidence, and explanation. | P0 |
| FR-07.2 | History SHALL be paginated (default 50, max 100 per page). | P1 |
| FR-07.3 | Individual events SHALL be retrievable by UUID. | P0 |

---

## 7. Non-Functional Requirements

### NFR-01: Performance

| ID | Requirement | Target |
|:---|:---|:---|
| NFR-01.1 | Rule Engine grading latency | < 50 ms |
| NFR-01.2 | ML inference latency (Decision Tree) | < 5 ms |
| NFR-01.3 | API response time (P95) | < 200 ms |
| NFR-01.4 | Frontend initial page load | < 3 seconds |
| NFR-01.5 | Offline grading operation | < 500 ms (IndexedDB write) |

### NFR-02: Scalability

| ID | Requirement | Target |
|:---|:---|:---|
| NFR-02.1 | Concurrent API connections | ≥ 100 simultaneous users |
| NFR-02.2 | Database event storage | ≥ 1,000,000 grading events |
| NFR-02.3 | Horizontal scaling support | Docker + Kubernetes ready |

### NFR-03: Availability & Reliability

| ID | Requirement | Target |
|:---|:---|:---|
| NFR-03.1 | Backend uptime (online mode) | 99.5% |
| NFR-03.2 | Offline mode availability | 100% (PWA cached) |
| NFR-03.3 | Zero data loss on network transitions | Guaranteed via IndexedDB queue |

### NFR-04: Security

| ID | Requirement | Target |
|:---|:---|:---|
| NFR-04.1 | EXIF metadata stripped before transmission | 100% |
| NFR-04.2 | Input validation on all API endpoints | Pydantic v2 + Zod |
| NFR-04.3 | Secrets excluded from version control | `.env` + `.gitignore` |
| NFR-04.4 | Docker containers run as non-root | `appuser` configured |

### NFR-05: Accessibility

| ID | Requirement | Target |
|:---|:---|:---|
| NFR-05.1 | Touch target minimum size | ≥ 48px × 48px |
| NFR-05.2 | High contrast for outdoor visibility | Civic Color Palette |
| NFR-05.3 | Keyboard navigation support | All interactive elements focusable |
| NFR-05.4 | ARIA labels on all form controls | Required |

---

## 8. System Architecture

### 8.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (PWA)                            │
│  React 19 + Vite + TypeScript + TailwindCSS                     │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────────┐    │
│  │ UI Pages │  │ TanStack     │  │ IndexedDB              │    │
│  │ (7 pages)│  │ Query v5     │  │ (ELHGS_Offline_DB)     │    │
│  └──────────┘  └──────┬───────┘  └───────────┬────────────┘    │
│                       │                       │                  │
│                       │    Service Worker      │                 │
│                       └───────┬───────────────┘                  │
└───────────────────────────────┼──────────────────────────────────┘
                                │ HTTP/REST
┌───────────────────────────────┼──────────────────────────────────┐
│                         SERVER (API)                             │
│  FastAPI + Python 3.13 + SQLAlchemy 2.x                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐    │
│  │ API Routes │  │ Services   │  │ Repositories           │    │
│  │ (v1/)      │→ │ (Business  │→ │ (Data Access)          │    │
│  │            │  │  Logic)    │  │                        │    │
│  └────────────┘  └─────┬──────┘  └───────────┬────────────┘    │
│                        │                      │                  │
│              ┌─────────┴──────────┐           │                  │
│              │                    │           │                  │
│       ┌──────┴──────┐    ┌───────┴───┐       │                  │
│       │ Rule Engine │    │ ML Layer  │       │                  │
│       │ (Baseline)  │    │ (Advisory)│       │                  │
│       └─────────────┘    └───────────┘       │                  │
└──────────────────────────────────────────────┼──────────────────┘
                                               │
                              ┌────────────────┴───────────────┐
                              │       PostgreSQL 18            │
                              │    Star Schema Database        │
                              │  ┌────────────────────────┐   │
                              │  │  fact_grading_events    │   │
                              │  │    ↕        ↕     ↕     │   │
                              │  │ dim_sample dim_grader   │   │
                              │  │ dim_image  dim_criterion│   │
                              │  └────────────────────────┘   │
                              └────────────────────────────────┘
```

### 8.2 Technology Stack

| Layer | Technology | Version |
|:---|:---|:---|
| **Frontend Framework** | React | 19.x |
| **Build Tool** | Vite | 5.x |
| **Language (Frontend)** | TypeScript | 5.x |
| **CSS Framework** | TailwindCSS | 3.x |
| **Data Fetching** | TanStack Query | 5.x |
| **Backend Framework** | FastAPI | 0.115.x |
| **Language (Backend)** | Python | 3.13 |
| **ORM** | SQLAlchemy | 2.x |
| **Schema Validation** | Pydantic | 2.x |
| **Database** | PostgreSQL | 18.x |
| **Migrations** | Alembic | 1.x |
| **Machine Learning** | scikit-learn | 1.x |
| **Containerization** | Docker + Docker Compose | Latest |
| **CI/CD** | GitHub Actions | Latest |

---

## 9. Data Model

### 9.1 Star Schema Design

The database follows a **Star Schema** optimized for analytical queries and audit compliance.

#### Fact Table

**`fact_grading_events`** — Central transaction table recording every grading evaluation.

| Column | Type | Description |
|:---|:---|:---|
| `id` | UUID (PK) | Unique event identifier |
| `sample_id` | UUID (FK → dim_sample) | Reference to the livestock sample |
| `grader_id` | UUID (FK → dim_grader) | Reference to the human grader |
| `image_id` | UUID (FK → dim_image) | Reference to the uploaded image |
| `criterion_id` | UUID (FK → dim_criterion) | Reference to the grading criteria used |
| `human_grade` | VARCHAR | The human grader's final grade (A/B/C/D) |
| `ai_grade` | VARCHAR | The system-calculated grade (A/B/C/D) |
| `confidence_score` | FLOAT | System confidence percentage (0–100) |
| `explanation` | TEXT (JSON) | Serialized plain-text explanation |
| `review_status` | VARCHAR | `pending` / `approved` / `disputed` |
| `client_offline_id` | VARCHAR | Client-side UUID for offline deduplication |
| `is_synced` | BOOLEAN | Whether the event has been synced from offline |
| `created_at` | TIMESTAMP | Event creation timestamp |
| `updated_at` | TIMESTAMP | Last modification timestamp |
| `deleted_at` | TIMESTAMP | Soft-delete timestamp (nullable) |

#### Dimension Tables

| Table | Key Columns | Purpose |
|:---|:---|:---|
| `dim_sample` | `id`, `species`, `breed`, `age_months`, `weight_kg`, `tag_number` | Livestock identity |
| `dim_grader` | `id`, `name`, `certification_level`, `region` | Human grader identity |
| `dim_image` | `id`, `file_path`, `file_size`, `mime_type`, `exif_stripped` | Image evidence with privacy audit |
| `dim_criterion` | `id`, `name`, `version`, `description` | Grading rubric version tracking |

---

## 10. API Specification

**Base URL:** `http://localhost:8000/api/v1`

| Method | Endpoint | Description | Auth |
|:---|:---|:---|:---:|
| `GET` | `/health` | Service health check | None |
| `POST` | `/grade` | Submit attributes and receive explainable grade | None* |
| `GET` | `/grading-events` | Paginated grading history | None* |
| `GET` | `/grading-events/{id}` | Single event by UUID | None* |
| `GET` | `/disagreements` | List all flagged disagreements | None* |
| `GET` | `/metrics` | Real-time aggregate KPIs | None* |
| `POST` | `/sync` | Sync offline-queued events | None* |

*\* Authentication is a placeholder for production deployment. The current hackathon version operates without auth for demo accessibility.*

### 10.1 Grade Request Schema

```json
{
  "attributes": {
    "body_condition": 3.0,
    "coat_quality": "Smooth",
    "eye_condition": "Clear",
    "wound_presence": "None",
    "mobility": "Normal",
    "appetite": "Good"
  },
  "sample_id": "uuid-or-null",
  "grader_id": "uuid-or-null",
  "image_id": "uuid-or-null",
  "human_grade": "A"
}
```

### 10.2 Grade Response Schema

```json
{
  "status": "success",
  "message": "Grade calculated successfully.",
  "data": {
    "grade": "A",
    "confidence": 100.0,
    "reasons": [
      "Body condition is optimal",
      "Coat quality is smooth",
      "Eye condition is clear",
      "Wound presence is none",
      "Mobility is normal",
      "Appetite is good",
      "Final Grade: A (Average of sub-grades)"
    ],
    "missing_attributes": [],
    "review_required": false,
    "disagreement": null
  }
}
```

---

## 11. Rule Engine Specification

### 11.1 Attribute Rubric Mappings

#### Body Condition Score (BCS) — Numeric (1.0–5.0)

| BCS Range | Grade | Reason |
|:---:|:---:|:---|
| 2.5 – 3.5 | A | Optimal body condition |
| 2.0 – 2.49 or 3.51 – 4.0 | B | Slightly under/overweight |
| 1.5 – 1.99 or 4.01 – 4.5 | C | Poor body condition |
| < 1.5 or > 4.5 | D | Emaciated or dangerously obese |

#### Categorical Attributes

| Attribute | Grade A | Grade B | Grade C | Grade D |
|:---|:---|:---|:---|:---|
| **Coat Quality** | Smooth | Slightly rough | Rough | Severe lesions |
| **Eye Condition** | Clear | Slight discharge | Cloudy | Severe infection |
| **Wound Presence** | None | Minor | Moderate | Severe |
| **Mobility** | Normal | Slight limp | Lame | Unable to stand |
| **Appetite** | Good | Fair | Poor | None |

### 11.2 Rule Hierarchy (Execution Order)

```
1. Critical Failure Rule (highest priority)
   └─ IF any attribute = Grade D → Final Grade = D

2. Warning Threshold Rule
   └─ IF ≥ 2 attributes = Grade C → Final Grade ≤ C (capped)

3. Average Calculation (default)
   └─ Average numeric sub-grades → Map to nearest letter grade
      ├─ avg ≤ 1.5 → A
      ├─ avg ≤ 2.5 → B
      ├─ avg ≤ 3.5 → C
      └─ avg > 3.5 → D
```

---

## 12. Machine Learning Specification

### 12.1 Model Registry

| Model | Algorithm | Purpose | Status |
|:---|:---|:---|:---|
| **Primary** | Decision Tree Classifier | Advisory grade prediction | Deployed |
| **Comparison** | Logistic Regression | Linear baseline benchmark | Deployed |

### 12.2 Feature Set

Input features derived from the 6 physical observation attributes:
- `body_condition` (float, 1.0–5.0)
- `coat_quality` (categorical, 4 levels)
- `eye_condition` (categorical, 4 levels)
- `wound_presence` (categorical, 4 levels)
- `mobility` (categorical, 4 levels)
- `appetite` (categorical, 4 levels)

### 12.3 Benchmark Results

| Model | Accuracy | F1-Score | Inference Speed |
|:---|:---:|:---:|:---:|
| **Rule Engine (Baseline)** | 64.67% | 66.89% | 0.045 ms |
| **Decision Tree Classifier** | **88.17%** | **88.22%** | **0.004 ms** |
| **Logistic Regression** | 67.83% | 68.32% | 0.008 ms |

*All benchmark figures above are `[measured, 600 synthetic samples]`. On the N=32 real validation set, the Rule Engine (κ=0.63, 71.9% match) outperforms the Decision Tree ML (κ=0.30, 53.1% match) due to synthetic training heuristic distribution mismatch. See `docs/dataset_protocol.md` for details.*

### 12.4 Explainability

- Decision Tree provides **feature importance ranking** (e.g., Wound Presence: 42.1%, BCS: 28.3%).
- Decision paths are extractable for any individual prediction.
- No black-box opacity — intentional avoidance of deep learning architectures.

---

## 13. Offline & Sync Specification

### 13.1 Offline Storage

| Component | Technology | Purpose |
|:---|:---|:---|
| Database | IndexedDB (`ELHGS_Offline_DB`) | Store queued grading events |
| Caching | Service Worker (`sw.js`) | Cache application shell for offline launch |
| Image Processing | HTML5 Canvas | Client-side EXIF stripping and compression |

### 13.2 Two-Stage Sync Protocol

```
Stage 1: Lightweight Attribute Sync
  └─ POST /api/v1/sync
     ├─ Payload: JSON attributes + grades (< 1 KB)
     └─ Network: Works on 2G/3G cellular

Stage 2: Image Upload
  └─ POST /api/v1/sync (with image data)
     ├─ Payload: Compressed JPEG/WebP (< 500 KB)
     └─ Network: Requires 3G+ cellular or Wi-Fi
```

### 13.3 Conflict Resolution

- **Client-side UUID deduplication** via `client_offline_id` prevents duplicate event creation.
- **Last-write-wins** strategy for concurrent modifications.
- **Automatic retry** with exponential backoff on network failures.

---

## 14. Security & Privacy Requirements

### 14.1 Privacy Controls

| Control | Implementation | Status |
|:---|:---|:---:|
| EXIF/GPS stripping | Client-side HTML5 canvas redraw | ✅ Active |
| No worker surveillance | No location tracking or camera serial logging | ✅ Enforced |
| No employee ranking | System provides no individual performance metrics | ✅ By design |
| Data minimization | Only required attributes collected | ✅ Enforced |

### 14.2 Input Validation

| Layer | Technology | Scope |
|:---|:---|:---|
| Frontend | Zod schemas + React Hook Form | All form inputs validated before submission |
| Backend | Pydantic v2 models | All API payloads validated at deserialization |
| Database | PostgreSQL constraints | Column types, NOT NULL, FK integrity |

### 14.3 Infrastructure Security

| Control | Implementation |
|:---|:---|
| Container isolation | Multi-stage Docker builds with non-root `appuser` |
| Secret management | Environment variables via `.env` (excluded from git) |
| Dependency auditing | `npm audit` and `pip audit` in CI pipeline |
| CORS configuration | Configurable allowed origins (currently `*` for demo) |

---

## 15. UI/UX Requirements

### 15.1 Pages & Navigation

| Page | Route | Primary Function |
|:---|:---|:---|
| **Home** | `/` | Landing page with system overview and quick actions |
| **Capture Grade** | `/capture` | Input attributes, upload image, submit for grading |
| **Grading Result** | `/result` | Display grade, confidence, explanation, and disagreement status |
| **Grading History** | `/history` | Paginated table of all past grading events |
| **Disagreements** | `/disagreements` | Queue of flagged human-vs-system disagreements |
| **Metrics Dashboard** | `/metrics` | Real-time KPIs, model comparison charts |
| **Ethics & Limitations** | `/ethics` | Transparency page describing system boundaries |

### 15.2 Design System

- **Color Palette:** Civic Color Palette — Navy (#1B2A4A), Slate (#64748B), Teal (#0D9488), Emerald (#059669), Amber (#F59E0B), Rose (#F43F5E).
- **Typography:** System font stack with TailwindCSS defaults.
- **Touch Targets:** Minimum 48px × 48px for all interactive elements.
- **Responsiveness:** Mobile-first design from 360px to 1920px+ viewports.
- **Contrast:** High-contrast color combinations for outdoor sunlit visibility.

### 15.3 States

| State | Requirement |
|:---|:---|
| **Loading** | Skeleton loaders or spinner for all async operations |
| **Empty** | Informative empty states with call-to-action (e.g., "No grading events yet") |
| **Error** | Red error banner with descriptive message and "Try Again" button |
| **Offline** | Visual indicator of offline status; seamless queue behavior |
| **Success** | Green confirmation with grade result card |

---

## 16. Deployment & Infrastructure

### 16.1 Container Architecture

| Container | Base Image | Purpose |
|:---|:---|:---|
| `elhgs-backend` | python:3.13-slim (multi-stage) | FastAPI API server |
| `elhgs-frontend` | node:20 → nginx:alpine (multi-stage) | React PWA static serve |
| `elhgs-db` | postgres:18-alpine | PostgreSQL database |

### 16.2 Deployment Targets

| Platform | Service | Use Case |
|:---|:---|:---|
| Render / Railway | Backend API | Free-tier cloud hosting |
| Vercel | Frontend PWA | Static site hosting with CDN |
| Supabase / Neon | PostgreSQL | Managed free-tier database |
| Docker Compose | Full stack | Local development & demo |

### 16.3 CI/CD Pipeline

- **Trigger:** Push to `main` branch or Pull Request.
- **Steps:** Install dependencies → Run `pytest` (34 tests) → Build frontend → Report results.
- **Config:** `.github/workflows/ci.yml`.

---

## 17. Testing Strategy

### 17.1 Test Coverage

| Test Category | Count | Framework |
|:---|:---:|:---|
| Rule Engine unit tests | 3 | pytest |
| Confidence scoring tests | 4 | pytest |
| Explanation generation tests | 2 | pytest |
| Grading service integration tests | 5 | pytest |
| API endpoint tests (grading, history) | 5 | pytest + FastAPI TestClient |
| ML prediction tests | 2 | pytest |
| Model loading tests | 1 | pytest |
| Disagreement API tests | 1 | pytest |
| Metrics API tests | 1 | pytest |
| Sync API tests | 1 | pytest |
| Health API tests | 1 | pytest |
| Experiment framework tests | 3 | pytest |
| **Total** | **34** | **100% pass rate** |

### 17.2 Evaluation Framework

- **Controlled Simulation:** 2-arm trial comparing baseline (unassisted) vs. AI-assisted agreement rates across 200 synthetic grading trials.
- **Error Taxonomy:** 5-category classification (attribute interpretation, threshold boundary, missing data, fatigue-induced, random).

---

## 18. Risks & Mitigations

| # | Risk | Severity | Likelihood | Mitigation |
|:---:|:---|:---:|:---:|:---|
| R1 | Users trust AI grades blindly | High | Medium | Mandatory human confirmation; "AI Assisted" badge; Ethics page |
| R2 | ML model degrades with domain shift | Medium | Medium | Rule Engine baseline always available; model retraining pipeline |
| R3 | Offline sync data loss | High | Low | IndexedDB persistence; retry with exponential backoff; UUID dedup |
| R4 | EXIF stripping bypass | High | Low | Server-side validation of `exif_stripped` flag; no raw EXIF storage |
| R5 | Database performance at scale | Medium | Low | Star Schema indexing; connection pooling; read-replica support |
| R6 | Simulated results misrepresented | Medium | Medium | Explicit disclaimer on all reports and dashboard |

---

## 19. Release Plan

### v1.0.0 — Hackathon Edition (Current Release)

| Phase | Scope | Status |
|:---:|:---|:---:|
| 1 | Project scaffolding & planning | ✅ Complete |
| 2 | Database foundation (Star Schema) | ✅ Complete |
| 3 | Explainable Rule Engine | ✅ Complete |
| 4 | FastAPI REST API | ✅ Complete |
| 5 | React 19 PWA Frontend | ✅ Complete |
| 6 | Explainable ML Layer | ✅ Complete |
| 7 | Offline PWA & Two-Stage Sync | ✅ Complete |
| 8 | Evaluation & Experimentation | ✅ Complete |
| 9 | Deployment, CI/CD & Release | ✅ Complete |
| 10 | Presentation & Submission Package | ✅ Complete |

### Future Roadmap (Post-Hackathon)

| Version | Feature |
|:---|:---|
| v1.1.0 | JWT authentication & role-based access control |
| v1.2.0 | Edge camera integration for automated BCS detection |
| v1.3.0 | Multi-language support (regional dialects) |
| v2.0.0 | Expansion to sheep, swine, and poultry grading |

---

## 20. Appendices

### Appendix A: Glossary

| Term | Definition |
|:---|:---|
| **BCS** | Body Condition Score — numeric scale (1.0–5.0) measuring animal fat/muscle |
| **XAI** | Explainable Artificial Intelligence — AI systems whose outputs can be understood by humans |
| **PWA** | Progressive Web App — web application installable on devices with offline capability |
| **HITL** | Human-in-the-Loop — design pattern ensuring human authority over automated decisions |
| **Star Schema** | Data warehouse design with a central fact table surrounded by dimension tables |
| **EXIF** | Exchangeable Image File Format — metadata embedded in images (GPS, camera info) |

### Appendix B: Complete Project File Map (Exact Locations)

#### Root Files

| File | Exact Path |
|:---|:---|
| README | [README.md](file:///c:/Users/nallu/Desktop/livestock_farm/README.md) |
| PRD (This Document) | [PRD.md](file:///c:/Users/nallu/Desktop/livestock_farm/PRD.md) |
| License | [LICENSE](file:///c:/Users/nallu/Desktop/livestock_farm/LICENSE) |
| Changelog | [CHANGELOG.md](file:///c:/Users/nallu/Desktop/livestock_farm/CHANGELOG.md) |
| Release Notes | [RELEASE_NOTES.md](file:///c:/Users/nallu/Desktop/livestock_farm/RELEASE_NOTES.md) |
| Executive Summary | [EXECUTIVE_SUMMARY.md](file:///c:/Users/nallu/Desktop/livestock_farm/EXECUTIVE_SUMMARY.md) |
| Project Summary | [PROJECT_SUMMARY.md](file:///c:/Users/nallu/Desktop/livestock_farm/PROJECT_SUMMARY.md) |
| Project Statistics | [PROJECT_STATS.md](file:///c:/Users/nallu/Desktop/livestock_farm/PROJECT_STATS.md) |
| Submission Checklist | [SUBMISSION_CHECKLIST.md](file:///c:/Users/nallu/Desktop/livestock_farm/SUBMISSION_CHECKLIST.md) |
| Final Project Review | [FINAL_PROJECT_REVIEW.md](file:///c:/Users/nallu/Desktop/livestock_farm/FINAL_PROJECT_REVIEW.md) |
| Docker Compose | [docker-compose.yml](file:///c:/Users/nallu/Desktop/livestock_farm/docker-compose.yml) |
| Git Ignore | [.gitignore](file:///c:/Users/nallu/Desktop/livestock_farm/.gitignore) |
| Env Example | [.env.example](file:///c:/Users/nallu/Desktop/livestock_farm/.env.example) |
| Env Dev Example | [.env.development.example](file:///c:/Users/nallu/Desktop/livestock_farm/.env.development.example) |
| Env Prod Example | [.env.production.example](file:///c:/Users/nallu/Desktop/livestock_farm/.env.production.example) |

---

#### Documentation (`docs/`)

| Document | Exact Path |
|:---|:---|
| Architecture Guide | [architecture.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/architecture.md) |
| Database Design | [database.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/database.md) |
| API Documentation | [api.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/api.md) |
| Frontend Guide | [frontend.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/frontend.md) |
| ML Documentation | [machine_learning.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/machine_learning.md) |
| Offline Guide | [offline.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/offline.md) |
| Evaluation Report | [evaluation.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/evaluation.md) |
| Deployment Guide | [deployment.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/deployment.md) |
| User Guide | [user_guide.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/user_guide.md) |
| Admin Guide | [admin_guide.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/admin_guide.md) |
| Grading Rules | [grading_rules.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/grading_rules.md) |
| Grading Rubric | [grading_rubric.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/grading_rubric.md) |
| Requirements Spec | [requirements.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/requirements.md) |
| Ethics Policy | [ethics.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/ethics.md) |
| Limitations | [limitations.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/limitations.md) |
| Roadmap | [roadmap.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/roadmap.md) |
| Final Checklist | [final_checklist.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/final_checklist.md) |
| Presentation Outline | [presentation_outline.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/presentation_outline.md) |
| Judge Q&A Defense | [judge_questions.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/judge_questions.md) |
| Demo Script | [demo_script.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/demo_script.md) |
| Demo Video Guide | [demo_video.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/demo_video.md) |
| Poster Content | [poster_content.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/poster_content.md) |
| Comparison Report | [comparison_report.md](file:///c:/Users/nallu/Desktop/livestock_farm/docs/comparison_report.md) |

---

#### Backend — Application Entry & Configuration

| File | Exact Path |
|:---|:---|
| FastAPI Main Entry | [main.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/main.py) |
| App Settings | [settings.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/core/settings.py) |
| Logger Config | [logging.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/core/logging.py) |
| Alembic Config | [alembic.ini](file:///c:/Users/nallu/Desktop/livestock_farm/backend/alembic.ini) |
| Alembic Env | [env.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/alembic/env.py) |
| Backend Dockerfile | [Dockerfile](file:///c:/Users/nallu/Desktop/livestock_farm/backend/Dockerfile) |

---

#### Backend — Database Layer

| File | Exact Path |
|:---|:---|
| SQLAlchemy Base | [base.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/database/base.py) |
| DB Connection/Engine | [connection.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/database/connection.py) |
| Session Factory | [session.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/database/session.py) |

---

#### Backend — ORM Models (Star Schema)

| File | Exact Path |
|:---|:---|
| Models Init (exports) | [__init__.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/models/__init__.py) |
| Fact: Grading Event | [fact_grading_event.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/models/fact_grading_event.py) |
| Dim: Sample | [dim_sample.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/models/dim_sample.py) |
| Dim: Grader | [dim_grader.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/models/dim_grader.py) |
| Dim: Image | [dim_image.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/models/dim_image.py) |
| Dim: Criterion | [dim_criterion.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/models/dim_criterion.py) |
| Trained DT Model | [decision_tree.joblib](file:///c:/Users/nallu/Desktop/livestock_farm/backend/models/decision_tree.joblib) |
| Trained LR Model | [logistic_regression.joblib](file:///c:/Users/nallu/Desktop/livestock_farm/backend/models/logistic_regression.joblib) |

---

#### Backend — Pydantic Schemas

| File | Exact Path |
|:---|:---|
| API Request Schema | [api.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/schemas/api.py) |
| Grading Event Schema | [grading_event.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/schemas/grading_event.py) |
| Response Wrapper | [responses.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/schemas/responses.py) |
| Sample Schema | [sample.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/schemas/sample.py) |
| Grader Schema | [grader.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/schemas/grader.py) |
| Image Schema | [image.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/schemas/image.py) |
| Criterion Schema | [criterion.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/schemas/criterion.py) |

---

#### Backend — Rule Engine (`grading/`)

| File | Exact Path |
|:---|:---|
| Grade Constants | [constants.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/grading/constants.py) |
| Attribute Rubric Maps | [rubric.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/grading/rubric.py) |
| Rule Hierarchy Logic | [rules.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/grading/rules.py) |

---

#### Backend — Business Services (`services/`)

| File | Exact Path |
|:---|:---|
| Grading Service (Core) | [grading_service.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/services/grading_service.py) |
| API Grading Service | [api_grading_service.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/services/api_grading_service.py) |
| Rule Engine Wrapper | [rule_engine.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/services/rule_engine.py) |
| Confidence Calculator | [confidence.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/services/confidence.py) |
| Explanation Generator | [explanation.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/services/explanation.py) |
| Input Validators | [validators.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/services/validators.py) |
| Exception Handlers | [exceptions.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/services/exceptions.py) |

---

#### Backend — Repositories (Data Access)

| File | Exact Path |
|:---|:---|
| Grading Repository | [grading_repository.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/repositories/grading_repository.py) |
| Metrics Repository | [metrics_repository.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/repositories/metrics_repository.py) |

---

#### Backend — API Routes (`api/v1/`)

| File | Exact Path |
|:---|:---|
| Grading & History Routes | [grading.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/api/v1/grading.py) |
| Disagreements Route | [disagreements.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/api/v1/disagreements.py) |
| Metrics Route | [metrics.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/api/v1/metrics.py) |
| Sync Route | [sync.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/api/v1/sync.py) |

---

#### Backend — Machine Learning (`ml/`)

| File | Exact Path |
|:---|:---|
| ML Init | [__init__.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/ml/__init__.py) |
| Dataset Loader | [dataset_loader.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/ml/dataset_loader.py) |
| Feature Engineering | [feature_engineering.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/ml/feature_engineering.py) |
| Model Training | [train.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/ml/train.py) |
| Prediction Service | [predict.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/ml/predict.py) |
| Model Evaluation | [evaluation.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/ml/evaluation.py) |
| Model Comparison | [comparison.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/ml/comparison.py) |
| Model Registry | [model_registry.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/ml/model_registry.py) |

---

#### Backend — Evaluation & Experimentation (`evaluation/`)

| File | Exact Path |
|:---|:---|
| 2-Arm Experiment Runner | [experiment_runner.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/evaluation/experiment_runner.py) |
| Error Taxonomy Analyzer | [error_analyzer.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/evaluation/error_analyzer.py) |
| Report Generator | [report_generator.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/evaluation/report_generator.py) |

---

#### Backend — Middleware

| File | Exact Path |
|:---|:---|
| Request ID Middleware | [request_id.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/middleware/request_id.py) |
| Logging Middleware | [logging.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/middleware/logging.py) |

---

#### Backend — Test Suite (`tests/`) — 34 Passing

| File | Exact Path |
|:---|:---|
| Test Config / Fixtures | [conftest.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/conftest.py) |
| Rule Engine Tests (3) | [test_rule_engine.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/test_rule_engine.py) |
| Confidence Tests (4) | [test_confidence.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/test_confidence.py) |
| Explanation Tests (2) | [test_explanation.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/test_explanation.py) |
| Grading Service Tests (5) | [test_grading_service.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/test_grading_service.py) |
| Grading API Tests (5) | [test_grading_api.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/test_grading_api.py) |
| ML Prediction Tests (2) | [test_ml_prediction.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/test_ml_prediction.py) |
| Model Loading Tests (1) | [test_model_loading.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/test_model_loading.py) |
| Experiment Framework Tests (3) | [test_experiment_framework.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/test_experiment_framework.py) |
| Health API Test (1) | [test_health_api.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/test_health_api.py) |
| Metrics API Test (1) | [test_metrics_api.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/test_metrics_api.py) |
| Disagreements API Test (1) | [test_disagreements_api.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/test_disagreements_api.py) |
| Sync API Test (1) | [test_sync_api.py](file:///c:/Users/nallu/Desktop/livestock_farm/backend/tests/test_sync_api.py) |

---

#### Frontend — Application Shell

| File | Exact Path |
|:---|:---|
| App Entry | [main.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/main.tsx) |
| App Component | [App.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/App.tsx) |
| Global Styles | [index.css](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/index.css) |
| Route Definitions | [index.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/routes/index.tsx) |
| Root Layout | [RootLayout.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/layouts/RootLayout.tsx) |
| TypeScript Types | [index.ts](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/types/index.ts) |

---

#### Frontend — Pages (7)

| Page | Exact Path |
|:---|:---|
| Home Landing | [Home.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/pages/Home.tsx) |
| Capture Grade Form | [CaptureGrade.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/pages/CaptureGrade.tsx) |
| Grading Result | [GradingResult.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/pages/GradingResult.tsx) |
| Grading History | [GradingHistory.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/pages/GradingHistory.tsx) |
| Disagreement Review | [DisagreementReview.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/pages/DisagreementReview.tsx) |
| Metrics Dashboard | [MetricsDashboard.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/pages/MetricsDashboard.tsx) |
| Ethics & Limitations | [EthicsLimitations.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/pages/EthicsLimitations.tsx) |

---

#### Frontend — Reusable Components (17)

| Component | Exact Path |
|:---|:---|
| App Header | [AppHeader.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/AppHeader.tsx) |
| Sidebar Navigation | [Sidebar.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/Sidebar.tsx) |
| Bottom Navigation | [BottomNavigation.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/BottomNavigation.tsx) |
| Attribute Input Form | [AttributeForm.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/AttributeForm.tsx) |
| Image Uploader (EXIF Strip) | [ImageUploader.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/ImageUploader.tsx) |
| Grade Badge (A/B/C/D) | [GradeBadge.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/GradeBadge.tsx) |
| Confidence Progress Bar | [ConfidenceBar.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/ConfidenceBar.tsx) |
| Explanation Panel | [ExplanationPanel.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/ExplanationPanel.tsx) |
| KPI Metric Card | [KpiCard.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/KpiCard.tsx) |
| Conflict Dialog | [ConflictDialog.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/ConflictDialog.tsx) |
| Connection Indicator | [ConnectionIndicator.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/ConnectionIndicator.tsx) |
| Offline Banner | [OfflineBanner.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/OfflineBanner.tsx) |
| Pending Queue Card | [PendingQueueCard.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/PendingQueueCard.tsx) |
| Sync Status Badge | [SyncStatusBadge.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/SyncStatusBadge.tsx) |
| Empty State | [EmptyState.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/EmptyState.tsx) |
| Error State | [ErrorState.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/ErrorState.tsx) |
| Loading Spinner | [LoadingSpinner.tsx](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/components/LoadingSpinner.tsx) |

---

#### Frontend — Services & Utilities

| File | Exact Path |
|:---|:---|
| Axios API Client | [api.ts](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/services/api.ts) |
| Grading Service | [gradingService.ts](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/services/gradingService.ts) |
| History Service | [historyService.ts](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/services/historyService.ts) |
| Disagreement Service | [disagreementService.ts](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/services/disagreementService.ts) |
| Metrics Service | [metricsService.ts](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/services/metricsService.ts) |
| Offline Queue | [offlineQueue.ts](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/services/offlineQueue.ts) |
| Sync Manager | [syncManager.ts](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/services/syncManager.ts) |
| IndexedDB Local Database | [localDatabase.ts](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/utils/localDatabase.ts) |
| Image Optimizer (EXIF) | [imageOptimizer.ts](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/utils/imageOptimizer.ts) |
| Network Status Hook | [useNetworkStatus.ts](file:///c:/Users/nallu/Desktop/livestock_farm/frontend/src/hooks/useNetworkStatus.ts) |

---

#### Generated Reports (`reports/`)

| Report | Exact Path |
|:---|:---|
| Experiment Report | [experiment_report.md](file:///c:/Users/nallu/Desktop/livestock_farm/reports/experiment_report.md) |
| Model Comparison | [comparison_report.md](file:///c:/Users/nallu/Desktop/livestock_farm/reports/comparison_report.md) |
| Metrics Report | [metrics_report.md](file:///c:/Users/nallu/Desktop/livestock_farm/reports/metrics_report.md) |
| Stakeholder Validation | [stakeholder_validation.md](file:///c:/Users/nallu/Desktop/livestock_farm/reports/stakeholder_validation.md) |
| Limitations Report | [limitations_report.md](file:///c:/Users/nallu/Desktop/livestock_farm/reports/limitations_report.md) |

---

#### Dataset (`dataset/`)

| File | Exact Path |
|:---|:---|
| Dataset README | [README.md](file:///c:/Users/nallu/Desktop/livestock_farm/dataset/README.md) |

---

#### DevOps & CI/CD

| File | Exact Path |
|:---|:---|
| Docker Compose | [docker-compose.yml](file:///c:/Users/nallu/Desktop/livestock_farm/docker-compose.yml) |
| Backend Dockerfile | [Dockerfile](file:///c:/Users/nallu/Desktop/livestock_farm/backend/Dockerfile) |
| Docker Backend Alt | [backend.Dockerfile](file:///c:/Users/nallu/Desktop/livestock_farm/docker/backend.Dockerfile) |
| Docker Frontend Alt | [frontend.Dockerfile](file:///c:/Users/nallu/Desktop/livestock_farm/docker/frontend.Dockerfile) |
| GitHub Actions CI | [ci.yml](file:///c:/Users/nallu/Desktop/livestock_farm/.github/workflows/ci.yml) |
| Setup Script (Bash) | [setup.sh](file:///c:/Users/nallu/Desktop/livestock_farm/scripts/setup.sh) |
| Setup Script (PowerShell) | [setup.ps1](file:///c:/Users/nallu/Desktop/livestock_farm/scripts/setup.ps1) |
| Cleanup Script | [clean.sh](file:///c:/Users/nallu/Desktop/livestock_farm/scripts/clean.sh) |

### Appendix C: Simulation Disclaimer

> These results were obtained from a simulated evaluation framework using 200 representative grading trials based on the project's synthetic dataset and grading rubric. They are indicative of system potential but have not been validated with real-world livestock data.
