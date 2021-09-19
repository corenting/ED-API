from fastapi import APIRouter

from app import __version__
from app.models.health import Version

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/version", response_model=Version)
async def get_version() -> Version:
    """Get the current version of the app."""
    return Version(version=__version__)
