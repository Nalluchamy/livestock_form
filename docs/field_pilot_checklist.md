# Supervised Field Pilot Operational Checklist (Cattle Health & Condition)

> **MANDATORY CLINICAL DISCLAIMER:**
> **ELHGS condition grading is an observational decision-support score, not a veterinary medical diagnosis. Urgent cases require immediate clinical examination by a licensed veterinarian.**

---

## 1. Pilot Status & Scope

- **Deployment Phase:** Phase 12 Field Pilot Framework
- **Execution Status:** **PENDING STAKEHOLDER COHORT EXECUTION**
- **Target Species:** Beef and Dairy Cattle
- **Target Population:** Minimum 10 animals double-graded across minimum 2 independent ranches/feedlots.

---

## 2. Phase 1: Pre-Pilot Preparation (1–2 Weeks Prior)

- [ ] **Site Suitability & Safety Inspection:**
  - [ ] Confirm pen/chute safety for cattle and human handlers.
  - [ ] Ensure non-slip footing along evaluation alley.
  - [ ] Verify adequate, even lighting (minimum 500 lux diffuse or clear daylight).
- [ ] **Owner Informed Consent:**
  - [ ] Execute formal [Field Pilot Informed Consent Agreement](field_pilot_consent_form.md).
  - [ ] Verify data usage permissions (anonymized research imagery, zero public marketing).
- [ ] **Hardware & Device Readiness:**
  - [ ] Tablets/mobile devices installed with ELHGS PWA.
  - [ ] Camera lenses cleaned and test image resolution verified ($\ge 512\times 512$).
  - [ ] Device storage verified for offline queue operation (IndexedDB enabled).
- [ ] **Grader Onboarding:**
  - [ ] Review [Cattle Grading Rubric v2.0](cattle_grading_rubric_v2.md) with all graders.
  - [ ] Enforce double-blind isolation rule (Grader 1 and Grader 2 never share grades on site).
  - [ ] Emphasize the strict prohibition of inferring appetite or gait from static photos.

---

## 3. Phase 2: Live Pilot Day Execution

- [ ] **Animal Identification & Staging:**
  - [ ] Stage subject individually in inspection chute or alley.
  - [ ] Assign unique pilot code (`PILOT-SITE01-COW001`).
- [ ] **Direct Photo Capture:**
  - [ ] Capture perpendicular lateral profile ($90^\circ \pm 15^\circ$) showing entire body.
  - [ ] Verify absence of human faces, bystanders, or branded ranch signage.
  - [ ] Upload to ELHGS; verify automated EXIF scrubbing and 512x512 normalization.
- [ ] **Physical Examination & Log Recording:**
  - [ ] Record feed intake / rumination records from ranch bunk log (Appetite).
  - [ ] Observe locomotion across firm footing (Mobility / Locomotion score).
  - [ ] Weigh on calibrated platform scale if available.
- [ ] **Independent Double-Blind Grading:**
  - [ ] Grader 1 independently submits condition grade and structured attributes via PWA.
  - [ ] Grader 2 independently submits condition grade and structured attributes via PWA.
  - [ ] System automatically compares submissions:
    - If Match: Moves to `CONSENSUS_REACHED`.
    - If Conflicting: Preserves disagreement and alerts Senior Adjudicator queue.
- [ ] **Clinical Safety & Escalation Triage:**
  - [ ] If Grade D or severe wound / downer condition detected, immediately invoke [Clinical Escalation SOP](clinical_safety_and_escalation.md).

---

## 4. Phase 3: Post-Pilot Consolidation & Quality Audit

- [ ] **Queue Synchronization:**
  - [ ] Sync all offline cached assessments to central PostgreSQL database.
- [ ] **Senior Expert Adjudication:**
  - [ ] Review all flagged disagreements with attending veterinary lead.
  - [ ] Document clinical consensus rationales.
- [ ] **Stakeholder Feedback Intake:**
  - [ ] Administer [Pilot Feedback Survey](../data/field_pilot/pilot_feedback_template.json) to graders and ranch managers.
  - [ ] Record usability, rubric clarity, and workflow bottleneck ratings.
- [ ] **Dataset Versioning & Quality Certification:**
  - [ ] Run `dataset_versioning.py` to compile authoritative manifest and split manifests.
  - [ ] Update `docs/dataset_quality_report.md`.
