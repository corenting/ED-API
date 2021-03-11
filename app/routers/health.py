from fastapi import APIRouter

from app import __version__
from app.routers.responses.health import Version

router = APIRouter()


@router.get("/health/version", tags=["Health"], response_model=Version)
async def read_users() -> Version:
    return Version(version=__version__)
