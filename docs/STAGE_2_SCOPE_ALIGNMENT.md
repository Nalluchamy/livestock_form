# STAGE 2 SCOPE ALIGNMENT & ARCHITECTURAL CLARIFICATION

## 1. Executive Summary & Problem Statement Context

The competition problem statement specifies:
> *"A livestock farm needs an affordable way to monitor health and reduce disagreements between human quality graders. The requested prototype must demonstrate explainable produce-quality grading, disagreement review, project-created or ethically curated images, measurable attributes, expert grades, before-and-after experiments, confidence reporting, systematic error analysis, offline or low-bandwidth operation and a field-friendly data-capture workflow."*

### The Proctor's Finding: Scope & Domain Conflation
The problem statement contains a dual-domain description:
1. Operational farm setting ("livestock farm... monitor health").
2. Quality grading domain ("explainable produce-quality grading... human quality graders").

In Phases 1–14, development focused on cattle livestock health grading (Body Condition Scoring 1–5, mobility/lameness, clinical safety escalation, double-blind veterinary annotation). However, the proctor's Stage 2 review noted that:
> *"The requested prototype must demonstrate explainable produce-quality grading... Replace simulated synthetic data with genuine produce images and actual reference grades. Resolve the scope mismatch between produce-quality grading and the existing livestock-health implementation."*

---

## 2. Stage 2 Resolution Strategy

To directly satisfy the proctor's requirements without discarding 14 phases of verified production architecture (FastAPI backend, PostgreSQL persistence, Alembic migrations 0001–0004, RBAC auth, offline PWA, 133 passing automated tests):

### A. Tomato Quality Grading as Primary Stage 2 Demonstration
- **Selected Produce Commodity**: Fresh Market Tomatoes (*Solanum lycopersicum*).
- **Rationale**: Tomatoes provide objective, visually measurable surface criteria that can be assessed from smartphone photographs:
  - Color / Ripeness Stage (USDA 6-stage color classification: Green, Breaker/Turning, Pink, Light Red, Red).
  - Visible Bruising (impact damage, softening area as % of visible surface).
  - Surface Defects (growth cracks, blossom end rot, sunscald, insect blemishes).
  - Shape & Size Uniformity (aspect ratio, circularity, visible diameter).
  - Capture & Image Quality (illumination lux, focus/blur Laplacian variance, surface occlusion).
- **Provisional Grades**: Grade A (Premium Marketable), Grade B (Standard / Processing), Grade C (Cull / Reject).

### B. Clean Architectural Segregation (Zero Attribute Conflation)
Produce quality grading and livestock health monitoring are strictly segregated across code, schemas, and database records:

| Dimension | Produce Quality Grading (Primary Stage 2) | Livestock Health Monitoring (Segregated Secondary) |
| :--- | :--- | :--- |
| **Domain Entities** | Tomato / Vegetable Produce Lots | Cattle / Ruminant Livestock |
| **Grades** | Grade A (Premium), Grade B (Standard), Grade C (Cull) | BCS 1 (Emaciated) to BCS 5 (Obese); Health Tier 1–4 |
| **Visual Attributes** | Color stage, surface defect %, blemish area, bruising | Rib prominence, spine shelf, ocular discharge, lameness |
| **Rubric Engine** | `backend/grading/produce_rubric.py` & `produce_rules.py` | `backend/grading/rubric.py` & `cattle_grading_rubric_v2.md` |
| **Service Layer** | `ProduceGradingService` (`backend/services/produce_grading_service.py`) | `GradingService` (`backend/services/grading_service.py`) |
| **API Endpoints** | `/api/v1/produce/...` | `/api/v1/grade/...`, `/api/v1/real-assessment/...` |
| **Dataset Path** | `dataset/produce/{raw,processed,annotations,splits}` | `dataset/real/{raw,processed,annotations,splits}` |
| **Safety / Escalation** | Marketability downgrade, cull routing, review trigger | Clinical triage, veterinary emergency escalation |

No livestock attributes (e.g., BCS, spine shelf, ocular discharge) appear in produce grading payloads, and no produce attributes (e.g., blossom end rot, ripening stage) appear in livestock payloads.

---

## 3. Product Naming & Navigation Alignment

- **Product Name**: Explainable Quality Grading System (EQGS / ELHGS dual-engine platform).
- **Primary Stage 2 Interface**: Produce Quality Assessment Workspace (`/produce/grade`, `/produce/disagreements`, `/produce/experiments`).
- **Livestock Module Navigation**: Clearly labeled as *"Secondary Module: Livestock Health Assessment"* with dedicated route `/grade`. Graders and reviewers are never misled into assessing agricultural produce with veterinary rubrics or vice versa.

---

## 4. Administrative Scope-Confirmation Dependency

> [!WARNING] Scope Confirmation Dependency
> ant-grade has selected fresh market tomatoes as the primary produce commodity to fulfill the proctor's mandate for visually measurable produce-quality grading.
>
> If the competition evaluation committee or faculty proctor mandates an alternative produce commodity (e.g., apples, citrus, potatoes), the underlying `ProduceGradingService` is designed to be configurable with dynamic commodity rubrics.
> 
> Until formal proctor sign-off is received on tomato specifications, the tomato grading rubric is cataloged as a **Provisional Demonstration Standard**, requiring agricultural expert committee validation before commercial enforcement.
