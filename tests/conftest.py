"""
Pytest configuration and fixtures.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock
from fastapi import Request


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.
    
    Returns:
        TestClient: A test client for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def mock_request():
    """Create a mock request object."""
    return MagicMock(spec=Request)


# Use event_loop_policy fixture instead of redefining event_loop
@pytest.fixture(scope="session")
def event_loop_policy():
    """Return the default event loop policy."""
    return asyncio.DefaultEventLoopPolicy() 