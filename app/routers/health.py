from fastapi import APIRouter

from app import __version__
from app.models.health import Version
from app.routers.helpers.responses import dataclass_response

router = APIRouter()


@router.get("/health/version", tags=["Health"], response_model=Version)
@dataclass_response
async def get_version() -> Version:
    """Get the current version of the app."""
    return Version(version=__version__)
