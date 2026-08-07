from backend.core.settings import settings

def test_sync_batch_api(client):
    settings.DEMO_MODE = True
    payload = {
        "items": [
            {
                "id": "offline_101",
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
        ]
    }

    response = client.post("/api/v1/sync", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["processed_count"] == 1
    assert data["data"]["failed_count"] == 0

    settings.DEMO_MODE = False
