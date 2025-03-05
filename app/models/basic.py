"""
Basic models used throughout the application.
"""
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Response model for the root endpoint."""
    message: str = Field(..., example="Hello world!") 