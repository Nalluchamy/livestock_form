# Field Pilot Informed Consent & Data Governance Agreement

**Project Title:** Explainable Livestock Health Grading System (ELHGS) Supervised Field Pilot  
**Target Species:** Cattle (Beef & Dairy)  
**Governing Standard:** Agricultural AI Ethics & Non-Identifiable Livestock Research  

---

## 1. Purpose of the Study

The Explainable Livestock Health Grading System (ELHGS) is an AI-assisted condition grading system designed to support livestock producers, graders, and veterinarians by generating transparent, explainable recommendations based on observable physical traits.

This pilot evaluates system accuracy, usability, and inter-expert agreement against certified human livestock graders under real operational conditions.

---

## 2. Participant & Facility Responsibilities

By signing below, the facility owner or authorized manager agrees to:
1. Permit trained graders and researchers access to cattle handling facilities (chutes, pens, pastures) for visual inspection and non-invasive photography.
2. Provide access to daily feed intake records and calibrated scale weights where available.
3. Ensure safe handling of animals during visual assessment.

---

## 3. Data Governance & Privacy Protections

1. **Complete Anonymization:**
   All photographs taken during the pilot will have EXIF metadata (GPS coordinates, camera serial numbers, timestamps) stripped immediately upon ingestion.
2. **PII Filtering:**
   Images containing human faces, ranch brandings, license plates, or identifiable personal markers will be quarantined, flagged, and deleted or rejected from training datasets.
3. **Separate Provenance Records:**
   Facility identity, contact details, and signed consent forms are archived in a secure, non-public registry (`dataset/real/documentation/provenance_records.json`) completely separated from machine learning training features.
4. **No Commercial Marketing Use:**
   Collected imagery and scores are restricted exclusively to AI model evaluation, algorithmic explainability benchmarking, and academic/research dissemination.

---

## 4. Animal Welfare & Veterinary Care Disclaimer

- Participation in this visual evaluation poses zero physical risk to the livestock. Graders will not perform invasive procedures or administer medications.
- **ELHGS condition grading is an observational decision-support score, not a veterinary medical diagnosis. Urgent cases require immediate clinical examination by a licensed veterinarian.**
- The facility maintains sole authority over veterinary medical care and animal management.

---

## 5. Formal Consent & Authorization

**Facility / Ranch Name:** __________________________________________________  
**Authorized Manager / Owner:** _____________________________________________  
**Signature:** ____________________________________ **Date:** _______________  
**ELHGS Principal Investigator:** __________________ **Date:** _______________  
