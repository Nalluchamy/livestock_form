# 📖 User Guide

Welcome to the Explainable Livestock Health Grading System (ELHGS). This guide covers user workflows for Field Graders, Senior Reviewers, Farm Managers, and Buyers.

---

## 1. Field Grader Workflow (Offline & Online)
1. **Open App:** Access the ELHGS PWA on mobile or tablet.
2. **Capture Grade:** Tap **Grade** on the navigation bar.
3. **Capture Photo:** Take a livestock photograph (EXIF data and location metadata are automatically stripped for privacy).
4. **Input Attributes:**
   - Set **Body Condition Score (BCS)** (1.0 to 5.0).
   - Select Coat Quality, Eye Condition, Wound Presence, Mobility, and Appetite from friendly dropdowns.
5. **Calculate Grade:** Tap **Calculate Explainable Grade**.
6. **Offline Mode:** If internet connection is unavailable, the evaluation automatically saves to device IndexedDB storage and auto-syncs when returning to coverage.

---

## 2. Senior Reviewer Workflow
1. Navigate to **Disagreements** or **History**.
2. Filter for events marked **Disagreement** or **Review Required**.
3. Inspect plain-text decision rules and AI predictions.
4. Log manual override or confirm human decision without altering past data.

---

## 3. Farm Manager & Buyer Workflow
1. Open **Metrics Dashboard** to observe overall herd health agreement rates, average confidence scores, and pending reviews.
2. Inspect **Ethics & Guardrails** to review human-in-the-loop policies and data privacy guarantees.
