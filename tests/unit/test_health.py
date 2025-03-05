"""
Tests for the health endpoint.
"""

from fastapi import status


def test_health_check(client):
    """Test the health check endpoint returns the expected structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Check required fields
    assert "status" in data
    assert "version" in data
    assert "uptime_seconds" in data
    assert "uptime_human" in data
    assert "system" in data

    # Check system stats
    assert "process_id" in data["system"]
    assert "hostname" in data["system"]


def test_health_check_legacy(client):
    """Test the legacy health check endpoint returns the expected structure."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Check required fields
    assert "status" in data
    assert "version" in data
    assert "uptime_seconds" in data
    assert "uptime_human" in data
    assert "system" in data
