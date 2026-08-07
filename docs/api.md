# ELHGS API Documentation

The Explainable Livestock Health Grading System exposes a standard REST API powered by FastAPI.

## Base URL
All API endpoints are prefixed with `/api/v1`.

## Standard Response Format
Every endpoint returns a consistent wrapper structure:
```json
{
  "status": "success",
  "message": "Human readable message.",
  "data": { ... }
}
```

In the event of an error (e.g., 400 Bad Request, 422 Unprocessable Entity, 500 Internal Server Error), the `status` will be `"error"` and `data` will contain the validation or error details.

---

## Endpoints

### 1. Health Check
`GET /api/v1/health`

Verifies that the backend API is running and responding.

**Response (200 OK)**
```json
{
  "status": "success",
  "message": "Service is healthy",
  "data": {
    "status": "healthy",
    "version": "0.1.0"
  }
}
```

---

### 2. Submit Grading Event
`POST /api/v1/grade`

Runs the deterministic Rule Engine against the provided attributes. If `DEMO_MODE` is enabled in `settings.py`, providing a `sample_id` and `grader_id` is optional; they will be mocked automatically.

**Request Body**
```json
{
  "sample_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", 
  "grader_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "human_grade": "A",
  "attributes": {
    "body_condition": 3.0,
    "coat_quality": "Smooth",
    "eye_condition": "Clear",
    "wound_presence": "None",
    "mobility": "Normal",
    "appetite": "Good"
  }
}
```

**Response (200 OK)**
```json
{
  "status": "success",
  "message": "Grade calculated successfully.",
  "data": {
    "grading_event_id": "12345678-1234-5678-1234-567812345678",
    "grade": "A",
    "confidence": 100.0,
    "reasons": [
      "Passed (A): Optimal body condition",
      "Passed (A): Coat quality is smooth"
    ],
    "missing_attributes": [],
    "review_required": false,
    "sample_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "grader_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "generated_demo_entities": false
  }
}
```

---

### 3. Log a Disagreement
`POST /api/v1/disagreements`

Logs an explicit disagreement for Senior Review. *(Note: The `/grade` endpoint automatically flags disagreements when `human_grade` differs from the system grade. This endpoint acts as a manual override for frontends).*

**Request Body**
```json
{
  "human_grade": "B",
  "system_grade": "C",
  "reason": "Borderline body score"
}
```

**Response (200 OK)**
```json
{
  "status": "success",
  "message": "Disagreement logged successfully for Senior Review.",
  "data": {
    "disagreement_id": "...",
    "review_required": true
  }
}
```

---

### 4. Grading History
`GET /api/v1/grading-events?skip=0&limit=50`

Fetches a paginated history of all grading events.

**Response (200 OK)**
```json
{
  "status": "success",
  "message": "History retrieved successfully",
  "data": {
    "total": 124,
    "events": [
      {
        "id": "...",
        "human_grade": "A",
        "ai_grade": "A",
        "confidence_score": 100.0,
        "review_status": "completed",
        "created_at": "2024-03-20T14:00:00Z"
      }
    ]
  }
}
```

---

### 5. Aggregate Metrics
`GET /api/v1/metrics`

Returns aggregate system metrics for dashboards.

**Response (200 OK)**
```json
{
  "status": "success",
  "message": "Metrics retrieved successfully",
  "data": {
    "total_gradings": 124,
    "agreement_rate": 91.0,
    "disagreement_rate": 9.0,
    "average_confidence": 88.5,
    "pending_reviews": 4,
    "low_confidence_cases": 6
  }
}
```
