"""
Central router file that imports all routers from feature modules.
"""

from fastapi import APIRouter
from src.session.router import router as session_router
from src.workflow.router import router as workflow_router
from src.prompt.router import router as prompt_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include feature routers
api_router.include_router(session_router)
api_router.include_router(workflow_router)
api_router.include_router(prompt_router)

__all__ = ["api_router"]
