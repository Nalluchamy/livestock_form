import uuid
from backend.core.settings import settings


def test_grading_success_demo_mode(client):
    # Enable demo mode to auto-generate sample/grader IDs
    settings.DEMO_MODE = True
    
    payload = {
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
    
    response = client.post("/api/v1/grade", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    
    payload_data = data["data"]
    assert payload_data["grade"] == "A"
    assert payload_data["confidence"] == 100.0
    assert payload_data["generated_demo_entities"] is True
    assert "grading_event_id" in payload_data
    
    # Restore
    settings.DEMO_MODE = False


def test_grading_missing_required_ids_production_mode(client):
    settings.DEMO_MODE = False
    
    payload = {
        "attributes": {
            "body_condition": 3.0,
            "coat_quality": "Smooth",
            "eye_condition": "Clear",
            "wound_presence": "None",
            "mobility": "Normal",
            "appetite": "Good"
        }
    }
    
    response = client.post("/api/v1/grade", json=payload)
    assert response.status_code == 400
    
    data = response.json()
    assert data["status"] == "error"
    assert "Missing required sample_id or grader_id" in data["message"]


def test_grading_validation_error(client):
    settings.DEMO_MODE = True
    
    payload = {
        "attributes": {
            "body_condition": 99.0, # Invalid BCS
            "coat_quality": "Smooth",
            "eye_condition": "Clear",
            "wound_presence": "None",
            "mobility": "Normal",
            "appetite": "Good"
        }
    }
    
    response = client.post("/api/v1/grade", json=payload)
    assert response.status_code == 400
    
    data = response.json()
    assert data["status"] == "error"
    assert "Body condition must be between" in data["message"]
    
    settings.DEMO_MODE = False


def test_get_grading_history(client):
    # Just checking the endpoint returns 200 with the correct structure
    response = client.get("/api/v1/grading-events")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "total" in data["data"]
    assert "events" in data["data"]


def test_get_nonexistent_grading_event(client):
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/grading-events/{fake_id}")
    assert response.status_code == 404
    assert response.json()["message"] == "Grading event not found"
