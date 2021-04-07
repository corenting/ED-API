from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app import __version__
from app.routers import community_goals, galnet, health, ships
from app.database.database import Base, engine

from app.database.community_goal_status import CommunityGoalStatus
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ED-API",
    description="An API for Elite Dangerous 🌌.",
    version=__version__,
)


@app.exception_handler(Exception)
def exception_callback(*args: Any, **kwargs: Any) -> JSONResponse:
    """Register an exception callback for default exceptions."""
    return JSONResponse({"detail": "Unhandled error"}, status_code=500)


app.include_router(health.router)
app.include_router(galnet.router)
app.include_router(ships.router)
app.include_router(community_goals.router)
