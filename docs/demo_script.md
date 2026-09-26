# 🎬 ELHGS Live Demonstration & Walkthrough Script

> **Scope Statement:** ELHGS is an AI-assisted livestock health and condition grading system that provides explainable recommendations using non-identifiable images and measurable health attributes. It supports human graders and never replaces expert judgment.

---

## 📋 End-to-End Live Demonstration Flow

```
   [1. Open App] ──> [2. Capture Image] ──> [3. Input Attributes] ──> [4. Generate Grade]
                                                                            │
   [8. Dashboard Updates] <── [7. Senior Review] <── [6. Disagreement] <────┴──> [5. Read Explanation]
            │
            └──> [9. Offline Demo] ──> [10. Reconnect] ──> [11. Sync] ──> [12. Persistent Audit]
```

---

### Step 1: Open Application
- **Action:** Open `http://localhost` (or deployed PWA URL) in browser.
- **Talking Point:** *"Notice the clean, high-contrast civic interface designed specifically for outdoor field conditions with large tap targets and responsive mobile navigation. Our core principle is that ELHGS supports human graders and never replaces expert judgment."*

---

### Step 2: Capture Livestock Image
- **Action:** Navigate to **Grade**, tap the **Livestock Photograph** uploader, and upload an image.
- **Talking Point:** *"Notice the 'EXIF Privacy Stripped' green badge. All photo metadata, worker location tags, and timestamps are stripped client-side on HTML5 canvas and re-verified by server-side ingestion before storage, guaranteeing worker privacy."*

---

### Step 3: Enter Health Attributes
- **Action:** Input representative physical observations:
  - **Body Condition Score (BCS):** `3.0`
  - **Coat Quality:** `Smooth`
  - **Eye Condition:** `Clear`
  - **Wound / Injuries:** `None`
  - **Mobility:** `Normal`
  - **Appetite:** `Good`
  - *(Optional)* **Human Manual Grade:** Select `Grade B` (to demonstrate disagreement detection).

---

### Step 4: Generate Grade & View Confidence
- **Action:** Tap **Calculate Explainable Grade**.
- **Result:** The system evaluates the attributes in < 1ms and navigates to the **Grading Result** page.
- **Talking Point:** *"The system returns Grade A with 100% confidence. Notice that our Rule Engine baseline and Decision Tree ML advisory model both processed the data deterministically."*

---

### Step 5: Read Plain-Text Explanation
- **Action:** Scroll to **Explainable Decision Factors**.
- **Talking Point:** *"Instead of a black-box AI score, the system provides plain-text reasons: 'Passed (A): Optimal body condition', 'Passed (A): Coat quality is smooth'. Every decision is fully traceable."*

---

### Step 6: Create & Flag Disagreement
- **Action:** Observe the **Human Senior Review Recommended** alert banner (triggered because human entered `B` while system calculated `A`).
- **Talking Point:** *"Because the human field grader manually entered Grade B while the system calculated Grade A, ELHGS detects an inter-rater disagreement and queues it for senior review."*

---

### Step 7: Persistent Senior Review Queue & Adjudication
- **Action:** Navigate to **Disagreement Review**.
- **Talking Point:** *"Crucial Ethical Guardrail: The AI system NEVER overwrites human grader authority. In Phase 11, disagreements are persistently stored in PostgreSQL (`disagreement_reviews`). Original human and system grades are permanently immutable. Senior Reviewers can adjudicate records with clinical rationale and confirm final grades."*

---

### Step 8: Dynamic Live Dashboard
- **Action:** Navigate to **Metrics Dashboard**.
- **Talking Point:** *"Real-time analytics instantly update with live database counts: total gradings, agreement rates, pending reviews, resolved reviews, and grade distributions. Notice the explicit 'Pending Real-World Validation' badge for real data, avoiding any fabricated claims."*

---

### Step 9: Offline Demonstration
- **Action:** Open Chrome Developer Tools -> **Network** tab -> Check **Offline**.
- **Action:** Return to **Grade**, enter new attributes, and tap **Calculate Explainable Grade**.
- **Result:** **Offline Banner** appears: *"You are working offline. Grading decisions will save locally to IndexedDB."*
- **Talking Point:** *"Field officers operating on remote farms without cellular service can continue grading animals with zero interruption using native IndexedDB (`ELHGS_Offline_DB`)."*

---

### Step 10: Reconnect & Background Synchronization
- **Action:** Uncheck **Offline** in Developer Tools (re-enable network).
- **Result:** The **ConnectionIndicator** automatically turns green ("Online").
- **Talking Point:** *"Our two-stage low-bandwidth sync engine automatically synchronizes queued records with deduplication."*

---

### Step 11: Real Validation & Claim Transparency
- **Action:** Open the **Real-World Dataset** section on the Metrics Dashboard or view `reports/`.
- **Talking Point:** *"Finally, we maintain strict claim transparency: our simulated trial baseline demonstrated 71.8% dispute reduction under in-silico assumptions, while genuine field dispute reduction is ethically reported as 'Pending real-world validation' until partner field trials conclude."*
