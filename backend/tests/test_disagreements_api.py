def test_submit_disagreement(client):
    payload = {
        "human_grade": "B",
        "system_grade": "C",
        "reason": "Borderline body condition score."
    }
    
    response = client.post("/api/v1/disagreements", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "disagreement_id" in data["data"]
    assert data["data"]["review_required"] is True
