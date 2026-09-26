# EQGS REST API Reference Specification

**Project:** Explainable Quality Grading System (EQGS)  
**Primary Module:** Fresh-Market Produce Quality Grading (Tomatoes — Grade A/B/C)  
**Secondary Module:** Livestock Health Assessment (Cow/Goat/Sheep — Visual Signs)  
**Base URL:** `http://localhost:8000/api/v1`  
**Protocol:** HTTP/1.1 with JSON payloads and Multipart/form-data for file uploads  
**Authentication:** Bearer JWT Token (`Authorization: Bearer <token>`)  

---

## 1. Authentication & User Management

### 1.1 User Registration
- **Endpoint:** `POST /api/v1/auth/register`
- **Purpose:** Registers a new user account with specific organizational role.
- **Authentication:** Public (Disabled when registration is closed in production).
- **Request Body (JSON):**
  ```json
  {
    "username": "grader_jane",
    "email": "jane@packhouse.internal",
    "password": "SecurePassword2026!",
    "role": "EXPERT_GRADER"
  }
  ```
- **Responses:**
  - `201 Created`: User account provisioned.
  - `400 Bad Request`: Username or email already registered.
  - `422 Unprocessable Entity`: Password complexity requirements not satisfied.

### 1.2 User Login & Token Generation
- **Endpoint:** `POST /api/v1/auth/login`
- **Purpose:** Authenticates user credentials, returning access token and refresh token.
- **Authentication:** Public.
- **Request Body (JSON):**
  ```json
  {
    "username_or_email": "grader_jane",
    "password": "SecurePassword2026!"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "message": "Login successful",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "token_type": "bearer",
      "user": {
        "id": "7fa85f64-5717-4562-b3fc-2c963f66afa6",
        "username": "grader_jane",
        "role": "EXPERT_GRADER"
      }
    }
  }
  ```
- **Error Codes:**
  - `401 Unauthorized`: Invalid credentials or unverified account.
  - `403 Forbidden`: Account temporarily locked after 5 failed login attempts.

### 1.3 Get Current User Profile
- **Endpoint:** `GET /api/v1/auth/me`
- **Purpose:** Retrieves authenticated user identity, role, and permissions.
- **Authentication:** `Bearer <token>` (Any authenticated user).
- **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "data": {
      "id": "7fa85f64-5717-4562-b3fc-2c963f66afa6",
      "username": "grader_jane",
      "role": "EXPERT_GRADER",
      "is_active": true
    }
  }
  ```

---

## 2. Produce Quality Grading (Tomatoes — Primary Module)

### 2.1 Deterministic Produce Grading
- **Endpoint:** `POST /api/v1/produce/grade`
- **Purpose:** Evaluates produce attributes deterministically against the USDA/UNECE rule hierarchy.
- **Authentication:** Optional (Supports anonymous evaluation in demo mode).
- **Request Body (JSON):**
  ```json
  {
    "surface_defect_pct": 2.5,
    "ripeness_stage": "RED",
    "color_uniformity_pct": 92.0,
    "bruising_severity": "NONE",
    "shape_circularity": 0.88,
    "aspect_ratio": 1.02,
    "critical_defects": [],
    "laplacian_var": 145.0,
    "illumination_mean": 115.0,
    "surface_occlusion_pct": 0.0,
    "human_grade": "A"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "message": "Produce sample evaluated successfully.",
    "data": {
      "provisional_grade": "A",
      "confidence": 99.0,
      "confidence_type": "Deterministic Rule Clearance (Uncalibrated)",
      "image_quality_passed": true,
      "triggered_rules": [
        "RULE_SURFACE_DEFECT_GRADE_A",
        "RULE_RIPENESS_GRADE_A",
        "RULE_BRUISING_GRADE_A",
        "RULE_GEOMETRY_GRADE_A"
      ],
      "reasons": [
        "Surface defect area is minimal (2.5% <= 5.0%)",
        "Maturity RED with high color uniformity (92.0%)",
        "No visible mechanical bruising",
        "Symmetrical round fruit shape (circularity 0.88, AR 1.02)"
      ],
      "counterfactuals": [
        "Maintaining defect area below 5.0% preserves Grade A standing."
      ],
      "persistent_review_id": null
    }
  }
  ```

### 2.2 Image Upload & Automated Grading
- **Endpoint:** `POST /api/v1/produce/upload-and-grade`
- **Purpose:** Ingests raw produce photograph, scrubs EXIF metadata, extracts 10 visual attributes, and evaluates grade.
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file`: Image binary (JPEG, PNG, WebP)
  - `human_grade` *(optional)*: Grader's manual grade for agreement verification
- **Response `200 OK`:** Contains extracted features, optical quality clearance, provisional grade, and explanation.

### 2.3 Genuine Tomato Photo Ingestion
- **Endpoint:** `POST /api/v1/produce/upload-real`
- **Purpose:** Ingests genuine harvest photograph into `dataset/produce/real/raw/` with cryptographic and perceptual deduplication.
- **Authentication:** `Bearer <token>` (`EXPERT_GRADER`, `SENIOR_REVIEWER`, `ADMIN`).
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `file`: Image file (max 15 MB)
  - `collection_category`: Category (`apparent_high_quality`, `minor_visual_defects`, `substantial_defects`)
  - `sample_id` *(optional)*: Unique identifier
- **Responses:**
  - `200 OK`: Image ingested, dHash computed, and registered in `metadata.csv`.
  - `400 Bad Request`: Corrupted image or unsupported format.
  - `409 Conflict`: Image is an exact or near-perceptual duplicate ($d_H \le 4$).

### 2.4 Double-Blind Produce Annotation
- **Endpoint:** `POST /api/v1/produce/annotate-real`
- **Purpose:** Submits an independent expert grade for a genuine produce sample.
- **Authentication:** `Bearer <token>` (`EXPERT_GRADER`, `SENIOR_REVIEWER`, `ADMIN`).
- **Request Body (JSON):**
  ```json
  {
    "sample_id": "TOM-REAL-001",
    "grade": "A",
    "notes": "Firm skin, no shoulder russeting.",
    "attributes": {
      "surface_defect_pct": 2.0,
      "ripeness_stage": "RED"
    }
  }
  ```
- **Response `200 OK`:** Returns updated annotation record with current double-blind status (`PARTIALLY_ANNOTATED`, `CONSENSUS_REACHED`, or `DISAGREEMENT`).

### 2.5 Senior Disagreement Adjudication
- **Endpoint:** `POST /api/v1/produce/adjudicate-real`
- **Purpose:** Senior reviewer resolves conflicting grades between Grader 1 and Grader 2.
- **Authentication:** `Bearer <token>` (`SENIOR_REVIEWER`, `ADMIN`).
- **Request Body (JSON):**
  ```json
  {
    "sample_id": "TOM-REAL-003",
    "final_grade": "B",
    "rationale": "Micro-cracking on shoulder exceeds Grade A tolerance but is sound for processing."
  }
  ```

### 2.6 Real Produce Controlled Experiment
- **Endpoint:** `POST /api/v1/produce/real/experiment`
- **Purpose:** Runs controlled trial comparing unassisted vs AI-assisted produce grading.
- **Authentication:** `Bearer <token>` (`DATA_SCIENTIST`, `SENIOR_REVIEWER`, `ADMIN`).
- **Behavior:**
  - If consensus samples $< 10$: Returns `PENDING_REAL_DATA`.
  - If trial records $< 10$: Returns `PENDING_REAL_EXPERIMENT`.
  - If complete: Returns Cohen's kappa, observed agreement rate, and time savings.

### 2.7 Synthetic Produce Dataset Status
- **Endpoint:** `GET /api/v1/produce/synthetic-status`
- **Purpose:** Returns verification status of quarantined synthetic images in `dataset/produce/synthetic/`.
- **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "data": {
      "total_manifest_prompts": 320,
      "verified_on_disk": 6,
      "queued_quota": 314,
      "qc_passed": 3,
      "qc_review_flagged": 3,
      "is_synthetic": true,
      "quarantine_status": "STRICTLY_ISOLATED"
    }
  }
  ```

---

## 3. Disagreement Reviews & Adjudication (Secondary Module)

### 3.1 List Disagreement Reviews
- **Endpoint:** `GET /api/v1/reviews`
- **Purpose:** Retrieves paginated disagreement reviews with optional status filter.
- **Authentication:** `Bearer <token>` (`EXPERT_GRADER`, `SENIOR_REVIEWER`, `ADMIN`).
- **Query Parameters:**
  - `status`: Filter by status (`PENDING`, `IN_REVIEW`, `RESOLVED`, `ESCALATED`, `CANCELLED`)
  - `skip`: Pagination offset (default 0)
  - `limit`: Page size (default 50, max 100)
- **Response `200 OK`:** Paginated review objects with immutable original grades.

### 3.2 Resolve Disagreement Review
- **Endpoint:** `POST /api/v1/reviews/{review_id}/resolve`
- **Purpose:** Senior adjudicator submits authoritative binding decision.
- **Authentication:** `Bearer <token>` (`SENIOR_REVIEWER`, `ADMIN`).
- **Request Body (JSON):**
  ```json
  {
    "reviewer_action": "UPHELD_HUMAN",
    "reviewer_final_decision": "B",
    "reviewer_rationale": "Veterinary clinical assessment verified mild superficial dermatitis."
  }
  ```

---

## 4. Dataset Management & Provenance

### 4.1 Ingest Single Image
- **Endpoint:** `POST /api/v1/dataset/upload`
- **Purpose:** Uploads single livestock image with EXIF stripping, dHash computation, and PII masking.
- **Authentication:** `Bearer <token>` (`EXPERT_GRADER`, `SENIOR_REVIEWER`, `ADMIN`).
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file`: Image file
  - `sample_id` *(optional)*: Identifier
  - `source_type`: Collection source (`field_pilot`, `packhouse`)
  - `species`: Species (`cattle`, `goat`, `sheep`)

### 4.2 Batch Import ZIP Archive
- **Endpoint:** `POST /api/v1/dataset/upload/batch`
- **Purpose:** Ingests ZIP archive of photographs with Zip-Slip path traversal defense.
- **Authentication:** `Bearer <token>` (`EXPERT_GRADER`, `SENIOR_REVIEWER`, `ADMIN`).
- **Content-Type:** `multipart/form-data`

### 4.3 Get Dataset Provenance Records
- **Endpoint:** `GET /api/v1/dataset/provenance`
- **Purpose:** Retrieves audit log of all ingested image hashes, dimensions, and collection metadata.
- **Authentication:** `Bearer <token>` (`DATA_SCIENTIST`, `ADMIN`).

---

## 5. System Health & Observability

### 5.1 Basic Health Probe
- **Endpoint:** `GET /api/v1/health`
- **Purpose:** Kubernetes/Docker liveness probe returning DB connectivity and storage writeability.
- **Authentication:** Public.
- **Response `200 OK`:**
  ```json
  {
    "status": "healthy",
    "uptime_seconds": 1420.5,
    "database": {
      "connected": true,
      "latency_ms": 1.25,
      "dialect": "sqlite"
    },
    "storage": {
      "writable": true,
      "free_space_mb": 145200.0
    }
  }
  ```

### 5.2 Detailed Operational Monitoring
- **Endpoint:** `GET /api/v1/health/detailed`
- **Purpose:** Observability endpoint reporting authentication failure counts, token reuse alerts, and backup verification status.
- **Authentication:** Public.
