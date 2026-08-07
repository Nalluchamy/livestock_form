# 🛡️ Judge Q&A Technical Defense Guide

This guide provides authoritative, mathematically sound answers to anticipated technical questions from hackathon judges.

---

### Q1: Why did you build a Rule Engine instead of relying purely on Machine Learning?
**Answer:** In agricultural and veterinary domains, stakeholders refuse to adopt black-box statistical predictions without guaranteed safety rules. The Rule Engine establishes a deterministic, human-auditable baseline that guarantees critical failure criteria (e.g., severe wounds or inability to stand automatically force Grade D). The ML model acts as an advisory recommendation layer alongside it, not a replacement.

---

### Q2: Why did you choose a Decision Tree Classifier over Deep Learning (CNNs / ResNet)?
**Answer:** 
1. **Explainability:** Decision Trees are white-box models. We can extract exact feature importance percentages (e.g. *Wound presence: 42.1%*) and decision paths for every prediction.
2. **Dataset Size:** Deep learning requires tens of thousands of labeled images. Our Decision Tree achieves **88.17% accuracy** [measured, 600 synthetic samples] on structured physical observation attributes with minimal compute requirements.
3. **Inference Speed:** Decision Tree inference runs in **0.004 ms**, allowing instant execution on low-power mobile PWA devices.

---

### Q3: Why compare Logistic Regression against the Decision Tree?
**Answer:** Logistic Regression provides a linear baseline. Livestock health attributes involve non-linear step-function thresholds (e.g., a single severe wound drops the grade to D regardless of coat quality). Comparing both models proved that the Decision Tree's non-linear splits better capture domain logic, outperforming Logistic Regression (88.17% vs 67.83% Accuracy [measured, 600 synthetic samples]).

---

### Q4: Why is Human-in-the-Loop mandatory? Why not auto-grade animals?
**Answer:** Ethical and legal standards in livestock commerce require human accountability. ELHGS is explicitly an AI-assisted decision-support system. If a human grader and the system disagree, the app **never overwrites the human grade**. Instead, it flags the event for Senior Review, reducing dispute friction while preserving human authority.

---

### Q5: How does the Confidence Score calculation work?
**Answer:** Base confidence starts at 100% and is penalized deterministically:
- `-15%` for every missing attribute observation.
- `-20%` if no image is associated.
- `-20%` if observations contradict (e.g., Grade A attribute combined with Grade D attribute).
If confidence drops below 50%, the system automatically flags the evaluation for manual review.

---

### Q6: How does the PWA work in remote locations with zero internet?
**Answer:** The frontend is an offline-first PWA backed by native browser `window.indexedDB` (`ELHGS_Offline_DB`). When offline, evaluations save to an offline queue. When network connectivity is restored, a background sync engine processes queued events via two-stage low-bandwidth uploading (`POST /api/v1/sync`).

---

### Q7: How do you protect worker privacy?
**Answer:** When photos are selected in `ImageUploader.tsx`, a client-side HTML5 canvas redraws the image, stripping all EXIF geotags, GPS coordinates, and camera metadata before saving or transmitting. This prevents farm worker location surveillance.

---

### Q8: Why use a Star Schema in PostgreSQL?
**Answer:** The Star Schema (`fact_grading_events` surrounded by `dim_sample`, `dim_grader`, `dim_image`, `dim_criterion`) decouples transaction events from dimension entities. This enables rapid aggregation of agreement rates, historical audits, and analytics without complex multi-table join bottlenecks.

---

### Q9: How would you scale this system to production?
**Answer:**
1. **Infrastructure:** Deploy FastAPI via Docker on Kubernetes with horizontal auto-scaling (HPA).
2. **Database:** Migrate PostgreSQL to Managed AWS RDS with read-replicas.
3. **Storage:** Offload image storage to Amazon S3 with CloudFront CDN.
4. **Caching:** Add Redis for caching real-time metric aggregations.
