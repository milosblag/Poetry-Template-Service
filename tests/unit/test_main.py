"""
Tests for the main application module.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI

from app.core.config import get_settings
from app.main import lifespan

# Get settings
settings = get_settings()


@pytest.mark.asyncio
async def test_lifespan_normal():
    """Test the lifespan context manager under normal conditions."""
    # Create a mock FastAPI app
    mock_app = MagicMock(spec=FastAPI)

    # Mock the logger
    mock_logger = MagicMock()

    with patch("app.main.logger", mock_logger):
        # Create a flag to verify the yield was executed
        yield_executed = False

        # Use the lifespan context manager
        async with lifespan(mock_app):
            yield_executed = True

        # Verify that yield was executed and logging calls were made
        assert yield_executed
        assert mock_logger.info.call_count == 2
        # Check first call contains "starting up"
        assert any(
            "starting up" in args[0]
            for args, _ in mock_logger.info.call_args_list
        )
        # Check second call contains "shutting down"
        assert any(
            "shutting down" in args[0]
            for args, _ in mock_logger.info.call_args_list
        )


@pytest.mark.asyncio
async def test_lifespan_exception():
    """Test the lifespan context manager when an exception occurs during startup."""
    # Create a mock FastAPI app
    mock_app = MagicMock(spec=FastAPI)

    # Mock the logger
    mock_logger = MagicMock()

    with patch("app.main.logger", mock_logger):
        # Create a test exception
        test_error = ValueError("Test initialization error")

        # Check that the exception propagates and error is logged
        with pytest.raises(ValueError) as exc_info:
            async with lifespan(mock_app):
                raise test_error

        # Verify the exception and logging
        assert exc_info.value == test_error

        # Check that info is called twice - once for startup and once for shutdown
        assert mock_logger.info.call_count == 2
        mock_logger.info.assert_any_call(
            f"Application starting up in "
            f"{settings.ENVIRONMENT} environment..."
        )
        mock_logger.info.assert_any_call("Application shutting down...")

        # Check that error is logged once
        mock_logger.error.assert_called_once()
        error_msg = mock_logger.error.call_args[0][0]
        assert "Error during initialization" in error_msg
