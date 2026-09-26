# EQGS Error Boundaries & Fault Recovery Architecture

**Project:** Explainable Quality Grading System (EQGS)  
**Primary Module:** Fresh-Market Produce Quality Grading (Tomatoes — Grade A/B/C)  
**Secondary Module:** Livestock Health Assessment (Cow/Goat/Sheep — Visual Signs)  
**Scope:** Frontend Rendering Boundaries, Backend Exception Handling, and Data-Integrity Fault Isolation  

---

## 1. Architectural Overview

The **Explainable Quality Grading System (EQGS)** employs a multi-tiered defense-in-depth error-handling architecture designed to prevent unhandled application crashes, protect users against data loss, enforce strict zero-information-disclosure security policies, and maintain academic/scientific integrity under adverse operational conditions.

```
                           +------------------------------------------+
                           |           User / Client Browser          |
                           +------------------------------------------+
                                                |
                     +--------------------------+--------------------------+
                     | Frontend React 18 Multi-Level Error Boundaries      |
                     | - Global App Level (App.tsx)                        |
                     | - Route / Layout Level (RootLayout.tsx)             |
                     +-----------------------------------------------------+
                                                | HTTP Requests
                                                v
                     +-----------------------------------------------------+
                     | FastAPI Core Exception Middleware Pipeline          |
                     | - APIException Handler (Custom 400/404/422)         |
                     | - RequestValidationError Handler (Pydantic 422)     |
                     | - SQLAlchemyError Handler (Sanitized 500)           |
                     | - General Exception Handler (Zero-Leakage 500)      |
                     +-----------------------------------------------------+
                                                |
                     +--------------------------+--------------------------+
                     | Domain-Specific Fault Isolation & Safeguards        |
                     | - Image Ingestion: Corrupted / MIME format gates    |
                     | - Optical Quality Gate: Lux / Blur rejections       |
                     | - Deduplication: SHA-256 & dHash 409 Conflict       |
                     | - RBAC Middleware: 401 Unauthorized / 403 Forbidden |
                     | - Controlled Trials: N >= 10 sample size guards     |
                     +-----------------------------------------------------+
```

---

## 2. Frontend React Error Boundaries

Unexpected JavaScript runtime errors in React components can unmount the entire component tree, resulting in an unresponsive white screen. EQGS implements hierarchical React Error Boundaries using [`frontend/src/components/ErrorBoundary.tsx`](file:///d:/livestock_farm/frontend/src/components/ErrorBoundary.tsx):

### 2.1 Multi-Level Boundary Hierarchy

1. **Global Application-Level Boundary (`App.tsx`):**
   - Wraps the top-level `QueryClientProvider`, `AuthProvider`, and `RouterProvider`.
   - Catches catastrophic initialization faults or unhandled context exceptions.
   - Provides full-screen recovery actions: **Try Again** (resets state), **Reload Application**, and **Return to Dashboard**.

2. **Route / Page-Level Boundary (`RootLayout.tsx`):**
   - Wraps the main `<Outlet />` containing all child page views (`ProduceGrading`, `MetricsDashboard`, `ExpertAnnotation`, etc.).
   - If a complex chart, table, or DOM node throws during rendering, **the global navigation, sidebar, app header, and offline indicator remain fully functional**.
   - The user sees an in-page alert banner isolating the failure to that specific tab without interrupting active grading sessions or unsaved forms.

### 2.2 Sanitized Fallback UI & Security
- **Credential Redaction:** The component automatically scrubs tokens and sensitive parameters from rendered error strings using regex redaction:
  ```typescript
  const safeMessage = this.state.error?.message
    ? this.state.error.message.replace(/(?:key|token|secret|password|auth)=\S+/gi, '[REDACTED]')
    : 'An unexpected rendering fault occurred.';
  ```
- **Console Hygiene:** In production (`import.meta.env.PROD`), component stack traces and internal variables are suppressed from browser consoles.

---

## 3. Backend Exception Handling Architecture

All exceptions entering FastAPI are intercepted by centralized exception handlers registered in [`backend/main.py`](file:///d:/livestock_farm/backend/main.py) and defined in [`backend/services/exceptions.py`](file:///d:/livestock_farm/backend/services/exceptions.py):

| Exception Type | Intercepting Handler | HTTP Status | Response Contract |
| :--- | :--- | :--- | :--- |
| **`APIException`** | `api_exception_handler` | Configurable (400, 404, 409, 422) | `{"success": false, "message": "...", "data": {...}}` |
| **`RequestValidationError`** | `validation_exception_handler` | 422 Unprocessable Entity | `{"success": false, "message": "Validation Error", "data": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| **`SQLAlchemyError`** | `sqlalchemy_exception_handler` | 500 Internal Server Error | `{"success": false, "message": "Internal Server Error: Database operation failed."}` |
| **`Exception` (Unhandled)**| `general_exception_handler` | 500 Internal Server Error | `{"success": false, "message": "Internal Server Error: An unexpected error occurred."}` |

### 3.1 Zero-Information-Disclosure Policy
- **No Stack Traces in Responses:** Python tracebacks (`Traceback (most recent call last)`) are strictly logged on the server and never returned in HTTP response bodies.
- **SQL Sanitization:** Database errors (e.g. syntax errors, constraint violations, table names, connection timeouts) are caught and replaced with a uniform, generic message. Internal database structure and connection strings are never disclosed to the client.

---

## 4. Domain-Specific Error Handling & Recovery Protocols

The application handles 9 distinct failure modes across data ingestion, grading, security, and experimental workflows:

### 4.1 Invalid or Corrupted Image Uploads
- **Detection:** In [`backend/evaluation/ingestion.py`](file:///d:/livestock_farm/backend/evaluation/ingestion.py), `PIL.Image.open()` attempts to read image streams inside an isolated try-except block, followed by `img.verify()`.
- **Handling:** If the binary payload is truncated, corrupted, or non-decodable, the service intercepts `UnidentifiedImageError` or `ValueError` and raises an HTTP 400 Bad Request:
  ```json
  {
    "detail": "Corrupted or invalid image data: cannot identify image file"
  }
  ```
- **Recovery:** In the frontend `ImageUploader.tsx`, the drag-and-drop zone marks the preview with a red border, displays the validation error, and resets the input file buffer.

### 4.2 Unsupported File Formats
- **Detection:** Enforces MIME and format validation against `ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}`. Executables (`.exe`, `.sh`), documents (`.pdf`), and text files are rejected immediately before disk writing or processing.
- **Handling:** Returns HTTP 400 Bad Request with a clear message:
  ```json
  {
    "detail": "Unsupported image format. Allowed: JPEG, PNG, WEBP."
  }
  ```

### 4.3 Duplicate Images (Cryptographic & Perceptual)
- **Detection (Tier 1):** Exact duplicate detection via SHA-256 cryptographic digest matching against existing provenance records.
- **Detection (Tier 2):** Perceptual near-duplicate detection via 64-bit Difference Hash (dHash) with bitwise Hamming distance calculation. If $d_H \le 4$, the image is identified as a near-identical capture of an existing sample.
- **Handling:** Returns HTTP 409 Conflict with collision details:
  ```json
  {
    "detail": "Duplicate image detected: Perceptual near-duplicate (dHash distance 2 <= 4 to sample TOM-REAL-001)"
  }
  ```
- **Integrity Safeguard:** Prevents repeated uploads of the same produce item from corrupting train/val/test splits or biasing inter-grader agreement trials.

### 4.4 Poor Image Quality (Optical Quality Gate)
- **Detection:** Evaluates focus sharpness via Laplacian variance ($\text{Var}(\nabla^2 I)$) and illumination luminance ($L_{\text{mean}}$):
  - Minimum Focus Sharpness: $\text{Var}(\nabla^2 I) \ge 100.0$
  - Illumination Bounds: $40.0\text{ lux} \le L_{\text{mean}} \le 245.0\text{ lux}$
  - Surface Occlusion Limit: $\le 30.0\%$
- **Handling:** Rather than throwing an internal error, the optical quality gate safely marks `image_quality_passed: false`, sets `provisional_grade: "REJECTED_IMAGE"`, drops confidence to `0.0%`, and generates plain-language diagnostic reasons:
  ```json
  {
    "provisional_grade": "REJECTED_IMAGE",
    "confidence": 0.0,
    "image_quality_passed": false,
    "reasons": [
      "Image blur detected (Laplacian variance 34.2 < 100.0)",
      "Image severely under-illuminated (mean luminance 28.3 < 40.0 lux)"
    ],
    "review_required": true
  }
  ```
- **Recovery:** The UI renders an amber diagnostic warning banner instructing the user to retake the photo under adequate packhouse lighting.

### 4.5 Database Connection Failures
- **Detection:** In [`backend/database/connection.py`](file:///d:/livestock_farm/backend/database/connection.py), SQLAlchemy connection pooling employs reconnection retries (`pool_pre_ping=True`).
- **Handling:** If database connectivity drops completely during an active transaction, `SQLAlchemyError` or `OperationalError` is intercepted by `sqlalchemy_exception_handler`. The database session is safely rolled back, and the client receives a sanitized 500 error.
- **Observability:** Detailed error messages and connection timestamps are recorded in server logs (`logs/app.log`) for operational triage.

### 4.6 API Request Failures & Network Loss
- **Detection:** Frontend Axios instances monitor HTTP status codes and network disconnect events via `window.addEventListener('offline')`.
- **Handling:** The global `OfflineBanner.tsx` displays an alert informing the user that requests are queued locally. React Query queries pause automated refetching until network connectivity is restored.

### 4.7 Unauthorized Access & RBAC Violations
- **Detection:** Route-level dependency injection (`require_role(...)`) validates cryptographic JWT signatures, token expiration, account active status, and role privileges.
- **Handling:**
  - Missing or expired token: HTTP 401 Unauthorized (`{"detail": "Could not validate credentials"}`).
  - Insufficient role (e.g. Farmer attempting Senior Adjudication): HTTP 403 Forbidden (`{"detail": "Operation not permitted for role 'FARMER'"}`).
- **Brute-Force Lockout:** Users with 5 consecutive failed login attempts have their accounts locked for 15 minutes (`User.locked_until`).

### 4.8 Offline Synchronization Conflicts
- **Detection:** When synchronizing offline assessment records via `POST /api/v1/sync`, the server verifies incoming entity versions against server timestamps.
- **Handling:** If a record was modified by another grader while the user was offline, the endpoint returns HTTP 409 Conflict with both conflicting state representations.
- **Recovery:** The frontend displays [`ConflictDialog.tsx`](file:///d:/livestock_farm/frontend/src/components/ConflictDialog.tsx), presenting side-by-side differences and allowing the operator to explicitly choose "Keep Local Version" or "Accept Server Version".

### 4.9 Missing Expert Annotations & Controlled Trial Guards
- **Detection:** The controlled trial runner in [`backend/evaluation/real_produce_pipeline.py`](file:///d:/livestock_farm/backend/evaluation/real_produce_pipeline.py) checks the count of consensus-annotated genuine produce samples.
- **Handling:** If $N < 10$ consensus samples exist, the runner **refuses to execute simulated benchmarks**. Instead of crashing with a `ZeroDivisionError` on empty metrics arrays, it returns a structured payload:
  ```json
  {
    "status": "PENDING_REAL_DATA",
    "evaluation_type": "real_produce_validation",
    "message": "Insufficient consensus-annotated genuine produce samples (0 available, minimum 10 required; 10 additional eligible consensus samples required). Per non-fabrication principles, real-data evaluation remains in PENDING_REAL_DATA status until genuine evidence is collected.",
    "real_images_collected": 0,
    "consensus_samples_available": 0,
    "eligible_samples_remaining": 10
  }
  ```

---

## 5. Verification & Test Evidence

System error handling and boundaries are verified by **11 dedicated automated tests** in [`backend/tests/test_error_handling_and_boundaries.py`](file:///d:/livestock_farm/backend/tests/test_error_handling_and_boundaries.py):

```bash
.venv\Scripts\python -m pytest backend\tests\test_error_handling_and_boundaries.py
======================= 11 passed, 3 warnings in 5.97s ========================
```

- `test_api_exception_returns_clean_json`: PASS
- `test_validation_exception_structure`: PASS
- `test_sqlalchemy_exception_sanitization`: PASS (Confirms zero SQL/credential leakage)
- `test_general_exception_sanitization`: PASS (Confirms generic 500 without stack traces)
- `test_unauthenticated_request_rejection`: PASS (Confirms 401 on missing auth)
- `test_unauthorized_role_rejection`: PASS (Confirms 403 on role privilege boundary)
- `test_corrupted_image_upload_handling`: PASS (Confirms graceful 400 rejection)
- `test_unsupported_file_extension_rejection`: PASS (Confirms non-image blocking)
- `test_duplicate_image_conflict_rejection`: PASS (Confirms 409 Conflict detection)
- `test_optical_quality_gate_low_illumination`: PASS (Confirms optical gate rejection handling)
- `test_controlled_experiment_insufficient_samples_guard`: PASS (Confirms division-by-zero defense)
