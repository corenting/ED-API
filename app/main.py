from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.constants import STATIC_PATH
from app.database.database import Base, engine
from app.routers import community_goals, galnet, health, news, ships, systems

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


app.include_router(community_goals.router)
app.include_router(galnet.router)
app.include_router(health.router)
app.include_router(news.router)
app.include_router(ships.router)
app.include_router(systems.router)
app.mount(f"/{STATIC_PATH}", StaticFiles(directory=STATIC_PATH), name=STATIC_PATH)
