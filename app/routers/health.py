from fastapi import APIRouter

from app import __version__
from app.models.health import Version

router = APIRouter()


@router.get("/health/version", tags=["Health"], response_model=Version)
async def get_version() -> Version:
    """Get the current version of the app."""
    return Version(version=__version__)
