# 📹 Demo Video Recording & Script Guide

This guide details the recording sequence, voiceover script, and editing guidelines for producing a 5-7 minute demonstration video for ELHGS.

---

## ⏱️ Video Timeline (Target: 6 Minutes)

| Segment | Time | Focus |
| :--- | :--- | :--- |
| **1. Intro & Problem** | 0:00 - 1:00 | System introduction, dispute problem in livestock markets |
| **2. Live Grading Flow** | 1:00 - 2:30 | Photo upload, EXIF privacy stripping, BCS entry, explainable results |
| **3. Disagreement & Senior Review** | 2:30 - 3:30 | Human vs. AI grade mismatch, human-in-the-loop policy |
| **4. Offline PWA Demo** | 3:30 - 4:30 | DevTools offline toggle, IndexedDB queueing, auto-sync |
| **5. Dashboard & Reports** | 4:30 - 5:30 | Metrics dashboard, 3-way model comparison, markdown reports |
| **6. Outro & Tech Stack** | 5:30 - 6:00 | Architecture summary and closing remarks |

---

## 🎙️ Sample Voiceover Script

**Segment 1 (0:00):**  
*"Welcome. Today we are presenting the Explainable Livestock Health Grading System, or ELHGS. In livestock markets, subjective disagreements between human field graders cause up to 35% dispute rates, leading to financial loss and market friction. Traditional black-box AI models fail because veterinarians demand transparent reasoning, and field workers often lack cellular internet coverage."*

**Segment 2 (1:00):**  
*"ELHGS solves this with an explainable, offline-first PWA. Watch as I upload a livestock photo. Notice our client-side EXIF privacy stripper automatically removes camera metadata to protect farm workers from location surveillance. Next, I input physical attributes—BCS 3.0, smooth coat, and clear eyes—and tap Calculate Grade. In under a millisecond, our Rule Engine returns Grade A with 100% confidence and plain-text decision factors."*

**Segment 3 (2:30):**  
*"What happens if a human grader disagrees? If I enter Grade B manually while the system calculates Grade A, ELHGS flags the mismatch for Senior Review. Crucially, the AI NEVER overwrites human authority—it acts strictly as a decision-support advisory tool."*

**Segment 4 (3:30):**  
*"Now let me toggle Offline Mode in Chrome DevTools to simulate a remote pasture. When I submit a grade offline, the app seamlessly queues the data locally in native IndexedDB. Re-enabling the network automatically triggers our two-stage low-bandwidth sync engine."*

**Segment 5 (4:30):**  
*"Our Metrics Dashboard provides real-time visibility into agreement rates, confidence distributions, and 3-way model comparisons between our Rule Engine, Decision Tree (88.17% Accuracy [measured, 600 synthetic samples]), and Logistic Regression."*

**Segment 6 (5:30):**  
*"Built with React 19, FastAPI, SQLAlchemy, and scikit-learn, ELHGS proves that explainable AI and offline design can transform agricultural decision-making. Thank you!"*
