# Grader Field Instructions & Protocol (Cattle Health Grading)

> **MANDATORY CLINICAL DISCLAIMER:**
> **ELHGS condition grading is an observational decision-support score, not a veterinary medical diagnosis. Urgent cases require immediate clinical examination by a licensed veterinarian.**

---

## 1. Role & Objective

As an expert grader participating in the ELHGS supervised field pilot, your objective is to provide rigorous, unbiased condition scoring of cattle according to the [Cattle Grading Rubric v2.0](cattle_grading_rubric_v2.md).

You are evaluating animal physical condition to benchmark and validate the explainable grading system.

---

## 2. Image Capture Standards

When photographing the subject:

1. **Stance & Framing:**
   - Stand approximately 3 to 5 meters from the animal at a $90^\circ$ perpendicular angle to its flank.
   - The entire animal from poll to tailhead, and from spine to hooves, must be visible.
   - Ensure the animal is standing squarely with head upright.
2. **Lighting:**
   - Position yourself with sunlight behind you or ensure diffuse overhead lighting.
   - Avoid dark pen shadows obscuring the ribs, hooks, or spine.
3. **Privacy & Biosecurity:**
   - Never capture farm personnel, faces, clothing badges, or ranch signage.
   - If an accidental bystander appears, immediately flag the image for quality rejection.

---

## 3. Strict Boundary: Photo-Visible vs. Examination Required

| Visible in Photo | Physical Exam / Ranch Log Required |
| :--- | :--- |
| - Body Condition Score (ribs, spine, pin bones) | - **Appetite** (Check feed bunk intake log or rumination collar) |
| - Coat sheen, bald patches, mange crusts | - **Mobility** (Must watch animal walk 10+ paces on firm ground) |
| - Eye discharge, corneal cloudiness | - **Live Weight** (Record from calibrated chute scale) |
| - Open lacerations, swelling, abrasions | |

> [!CAUTION]
> **NEVER GUESS APPETITE FROM A PHOTOGRAPH.**
> An animal resting in a pen cannot be assumed to be eating normally. If bunk intake logs are unavailable, mark appetite as `Fair` or `Pending Verification` with an explicit clinical note.

---

## 4. Double-Blind Protocol Rules

1. **Independent Evaluation:**
   Do not converse with, signal, or glance at the screen of your fellow grader during assessment.
2. **Submit Without Discussion:**
   Submit your grade directly into the ELHGS app. The software isolates your score and prevents Grader 2 from seeing Grader 1's decision.
3. **Preserving Disagreements:**
   Do not attempt to negotiate a compromise if you suspect a difference. Disagreements are scientifically essential for measuring inter-rater reliability (Cohen's Kappa) and training the advisory AI engine.

---

## 5. Urgent Escalation Protocol

If you observe an animal that meets any of the following:
- Apparent severe distress or inability to rise ("downer" animal)
- Deep, purulent, or bleeding lacerations
- Severe emaciation ($\text{BCS} < 1.5$)
- Corneal perforation or severe infection

**ACTION:** Immediately notify the facility herd manager and on-call veterinarian, and ensure the system's `urgent_escalation` alert is acknowledged.
