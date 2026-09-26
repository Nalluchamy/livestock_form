# Clinical Safety, Escalation Protocol & Medical Disclaimer

> **MANDATORY CLINICAL DISCLAIMER:**
> **ELHGS condition grading is an observational decision-support score, not a veterinary medical diagnosis. Urgent cases require immediate clinical examination by a licensed veterinarian.**

---

## 1. Ethical & Regulatory Boundary: Observational Support vs. Diagnosis

The **Explainable Livestock Health Grading System (ELHGS)** is strictly engineered as a **decision-support and triage tool** for commercial livestock management, market readiness assessment, and husbandry prioritization. 

1. **Not a Veterinary Diagnosis:** 
   ELHGS evaluates phenotypic characteristics (BCS, hide condition, eye discharge, visible lacerations) against established livestock quality rubrics. It does not perform differential diagnoses, microbiological pathology, internal imaging, or pharmacotherapy prescription.
2. **Human Expert Primacy:**
   All automated outputs are advisory. Graders retain full authority to override system suggestions, and discrepancies are preserved without algorithmic erasure.

---

## 2. Mandatory Disclaimer Placement

To guarantee transparency and prevent misinterpretation, the following disclaimer string is deterministically injected into:
- All REST API grading responses (`clinical_disclaimer` field)
- Frontend livestock assessment summary cards
- Expert annotation and senior review dashboards
- Exported PDF/CSV field reports and audit logs

> *"Condition grade is an observational decision-support score, not a veterinary medical diagnosis. Urgent cases require immediate clinical examination by a licensed veterinarian."*

---

## 3. Urgent Clinical Escalation Triggers

The system automatically triggers an **URGENT CLINICAL ESCALATION** event (`urgent_escalation: true`) whenever any of the following clinical danger thresholds are satisfied:

| Trigger Condition | Clinical Indicator | Risk Assessment | Action Priority |
| :--- | :--- | :--- | :--- |
| **Grade D Overall** | Comprehensive condition failure | Imminent animal welfare or mortality risk | Immediate Isolation & Triage |
| **Severe External Wounds** | Open lacerations, necrotic abscesses, maggot strike, deep puncture | Risk of septic shock, gangrene, or systemic infection | Immediate Veterinary Intervention |
| **Immobility ('Unable to stand')** | Recumbent "downer" cow, pelvic fracture, severe hypocalcemia | Irreversible muscle necrosis, death within hours | Emergency Veterinary Callout |
| **Extreme Emaciation ($\text{BCS} < 1.5$)** | Severe cachexia, transverse process shelf, zero fat | Advanced malnutrition, chronic wasting, end-stage disease | Nutritional Emergency & Clinical Exam |
| **Morbid Obesity ($\text{BCS} > 4.5$)** | Massive patchy fat rolls, distended brisket | Severe risk of hepatic lipidosis, dystocia, or heat stress | Husbandry Triage |
| **Severe Eye Infection** | Corneal ulceration, perforation, purulent discharge | Infectious bovine keratoconjunctivitis (Pinkeye) or blindness | Immediate Medical Isolation |

---

## 4. Standard Operating Procedure for Escalation (SOP-ESC-01)

When an urgent clinical escalation is flagged:

```
[System / Grader Escalation Triggered]
                 │
                 ▼
  [1. Immediate Herd Segregation] ───> Move animal to clean, sheltered infirmary pen
                 │
                 ▼
  [2. On-Call Veterinarian Alert] ───> Dispatch dispatch ticket with telemetry & images
                 │
                 ▼
  [3. Senior Audit Record Created] ──> Logged in PostgreSQL disagreement_reviews / expert_annotations
                 │
                 ▼
  [4. Physical Examination by Vet] ──> Formal clinical diagnosis & treatment plan recorded
```

1. **Immediate Pen Segregation:**
   Isolate the subject from herd competition or transit pens into a soft-bedded, covered infirmary paddock with accessible fresh water.
2. **Notification Dispatch:**
   The ELHGS system automatically tags the record with `review_status: pending` and emits a high-priority banner on the dashboard.
3. **Veterinary Clinical Examination:**
   A licensed veterinarian performs physical palpation, temperature, heart rate, auscultation, and diagnostic sample collection.
4. **Authoritative Resolution:**
   The senior reviewer or attending veterinarian documents clinical findings and updates the resolution audit trail.
