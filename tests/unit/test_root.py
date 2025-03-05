"""
Tests for the root endpoint.
"""

from fastapi import status


def test_read_root(client):
    """Test the root endpoint returns the expected message."""
    response = client.get("/api/v1/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello world!"}


def test_read_root_legacy(client):
    """Test the legacy root endpoint returns the expected message."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello world!"}
