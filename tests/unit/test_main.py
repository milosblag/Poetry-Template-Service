"""
Tests for the main application module.
"""

import socket
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI

from app.core.config import get_settings
from app.main import find_available_port, lifespan

# Get settings
settings = get_settings()


def test_find_available_port_success():
    """Test find_available_port when the first port attempt succeeds."""
    # Create a mock context manager for socket
    mock_socket = MagicMock()
    mock_context = MagicMock()
    mock_socket.__enter__.return_value = mock_context

    with patch("socket.socket", return_value=mock_socket):
        # The function should return the first port it tries
        result = find_available_port(8000)
        assert result == 8000
        # Verify socket was created with the right parameters
        socket.socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        # Verify bind was called with the right parameters
        mock_context.bind.assert_called_once_with((settings.HOST, 8000))


def test_find_available_port_retry():
    """Test find_available_port when it needs to try multiple ports."""
    # First socket raises OSError, second one succeeds
    mock_socket1 = MagicMock()
    mock_context1 = MagicMock()
    mock_socket1.__enter__.return_value = mock_context1
    mock_context1.bind.side_effect = OSError()

    mock_socket2 = MagicMock()
    mock_context2 = MagicMock()
    mock_socket2.__enter__.return_value = mock_context2

    # Return different mock sockets on consecutive calls
    with patch("socket.socket", side_effect=[mock_socket1, mock_socket2]):
        result = find_available_port(8000)
        assert result == 8001  # Should return the second port it tries
        mock_context1.bind.assert_called_once_with((settings.HOST, 8000))
        mock_context2.bind.assert_called_once_with((settings.HOST, 8001))


def test_find_available_port_fallback():
    """Test find_available_port when all ports are unavailable."""
    # Create mock sockets that always raise OSError
    mock_sockets = []
    max_attempts = 3

    for _ in range(max_attempts):
        mock_socket = MagicMock()
        mock_context = MagicMock()
        mock_socket.__enter__.return_value = mock_context
        mock_context.bind.side_effect = OSError()
        mock_sockets.append(mock_socket)

    # Return the mocks for each call
    with patch("socket.socket", side_effect=mock_sockets):
        result = find_available_port(8000, max_attempts=max_attempts)
        assert result == 8000  # Should fallback to the original port

        # Verify each port was tried
        for i, mock_socket in enumerate(mock_sockets):
            mock_socket.__enter__.return_value.bind.assert_called_once_with(
                (settings.HOST, 8000 + i)
            )


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
            "starting up" in args[0] for args, _ in mock_logger.info.call_args_list
        )
        # Check second call contains "shutting down"
        assert any(
            "shutting down" in args[0] for args, _ in mock_logger.info.call_args_list
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
            f"Application starting up in {settings.ENVIRONMENT} environment..."
        )
        mock_logger.info.assert_any_call("Application shutting down...")

        # Check that error is logged once
        mock_logger.error.assert_called_once()
        assert "Error during initialization" in mock_logger.error.call_args[0][0]
