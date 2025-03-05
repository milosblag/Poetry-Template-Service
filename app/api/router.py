"""
API router to include all endpoint routers.
"""
from fastapi import APIRouter
from app.api.endpoints import root, health

# Create main router
api_router = APIRouter()

# Include all endpoint routers with appropriate prefixes and tags
api_router.include_router(root.router, tags=["root"])
api_router.include_router(health.router, tags=["health"]) 