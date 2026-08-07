# 🚀 Release Notes - ELHGS v1.0.0

The Explainable Livestock Health Grading System (ELHGS) v1.0.0 is an AI-assisted decision-support platform designed to reduce disputes between livestock health graders while maintaining absolute human authority.

---

## 🌟 Key Features
- **Deterministic Rule Engine Baseline:** Evaluates Body Condition Score (BCS), coat, eyes, wounds, mobility, and appetite to produce Grade A-D with plain-text explanation reasons.
- **Advisory Machine Learning Layer:** Deploys a white-box Decision Tree Classifier (88.17% Accuracy [measured, 600 synthetic samples]) alongside Logistic Regression to provide feature importance attributions.
- **Human-in-the-Loop & Disagreement Tracking:** Automatically flags inter-grader or AI-human mismatches for Senior Review without ever overwriting human expert authority.
- **Offline-First PWA:** Full offline functionality using native IndexedDB, automatic background sync, and two-stage low-bandwidth data uploads.
- **Privacy First:** Automatic client-side canvas EXIF metadata stripping prevents worker surveillance.
- **Production Ready:** Multi-stage Docker setup, GitHub Actions CI, and Render/Vercel compatibility.

---

## ⚠️ Known Limitations
- Machine Learning models are currently trained on synthetic representative datasets and should be retrained on real-world empirical data prior to commercial deployment.
- Offline image uploads are queued for broadband connectivity while attribute JSON is synced immediately.

---

## 🔮 Future Roadmap
- Integration with edge micro-cameras for automatic real-time BCS bounding box detection.
- Multi-language support for regional field officers.
