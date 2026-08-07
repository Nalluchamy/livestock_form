def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Service is healthy"
    assert data["data"]["status"] == "healthy"
    assert "version" in data["data"]
