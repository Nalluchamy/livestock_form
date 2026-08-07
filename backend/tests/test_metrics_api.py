def test_get_metrics(client):
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    
    metrics_data = data["data"]
    assert "total_gradings" in metrics_data
    assert "agreement_rate" in metrics_data
    assert "disagreement_rate" in metrics_data
    assert "average_confidence" in metrics_data
    assert "pending_reviews" in metrics_data
    assert "low_confidence_cases" in metrics_data
