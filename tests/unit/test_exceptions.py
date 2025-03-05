"""
Tests for the exception handling utilities.
"""
import pytest
import time
import json
from unittest.mock import patch, MagicMock
from fastapi.responses import JSONResponse
from app.utils.exceptions import UnicornException, unicorn_exception_handler, generic_exception_handler
from app.core.config import get_settings

# Get settings
settings = get_settings()


def test_unicorn_exception():
    """Test that UnicornException correctly stores the message."""
    message = "Test unicorn error"
    exc = UnicornException(message)
    assert exc.message == message


@pytest.mark.asyncio
async def test_unicorn_exception_handler(mock_request):
    """Test the unicorn exception handler."""
    # Create a test exception
    test_message = "Test unicorn error"
    exc = UnicornException(test_message)
    
    # Mock the logger
    mock_logger = MagicMock()
    
    with patch("app.utils.exceptions.logger", mock_logger):
        # Call the handler
        response = await unicorn_exception_handler(mock_request, exc)
        
        # Verify response properties
        assert isinstance(response, JSONResponse)
        assert response.status_code == 418
        
        # Parse the JSON content
        content = json.loads(response.body.decode())
        assert "message" in content
        assert f"Oops! {test_message}" == content["message"]
        
        # Verify logging occurred
        mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_generic_exception_handler_development(mock_request):
    """Test the generic exception handler in development environment."""
    # Create a test exception
    test_message = "Test generic error"
    exc = ValueError(test_message)
    
    # Mock logger and time
    mock_logger = MagicMock()
    mock_time = 12345
    
    with patch("app.utils.exceptions.logger", mock_logger):
        with patch("time.time", return_value=mock_time):
            # Set environment to development
            with patch("app.utils.exceptions.settings.ENVIRONMENT", "development"):
                # Call the handler
                response = await generic_exception_handler(mock_request, exc)
                
                # Verify response properties
                assert isinstance(response, JSONResponse)
                assert response.status_code == 500
                
                # Parse the JSON content
                content = json.loads(response.body.decode())
                assert "message" in content
                assert "Internal server error" == content["message"]
                assert "error_id" in content
                assert f"error-{mock_time}" == content["error_id"]
                assert "detail" in content
                assert test_message == content["detail"]
                assert "traceback" in content
                
                # Verify logging occurred
                assert mock_logger.error.call_count == 2


@pytest.mark.asyncio
async def test_generic_exception_handler_production(mock_request):
    """Test the generic exception handler in production environment."""
    # Create a test exception
    test_message = "Test generic error"
    exc = ValueError(test_message)
    
    # Mock logger and time
    mock_logger = MagicMock()
    mock_time = 12345
    
    with patch("app.utils.exceptions.logger", mock_logger):
        with patch("time.time", return_value=mock_time):
            # Set environment to production
            with patch("app.utils.exceptions.settings.ENVIRONMENT", "production"):
                # Call the handler
                response = await generic_exception_handler(mock_request, exc)
                
                # Verify response properties
                assert isinstance(response, JSONResponse)
                assert response.status_code == 500
                
                # Parse the JSON content
                content = json.loads(response.body.decode())
                assert "message" in content
                assert "Internal server error" == content["message"]
                assert "error_id" in content
                assert f"error-{mock_time}" == content["error_id"]
                
                # In production mode, detailed info should not be included
                assert "detail" not in content
                assert "traceback" not in content
                
                # Verify logging occurred
                assert mock_logger.error.call_count == 2 