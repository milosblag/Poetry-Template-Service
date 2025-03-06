"""
Tests for the health endpoint.
"""

from fastapi import status


def test_basic_health_check(client):
    """Test the basic health check endpoint returns the expected structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Check required fields for basic health check
    assert "status" in data
    assert data["status"] == "ok"
    
    # Ensure detailed fields are not present
    assert "version" not in data
    assert "uptime_seconds" not in data
    assert "system" not in data
