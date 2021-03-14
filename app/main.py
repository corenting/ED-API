from fastapi import FastAPI

from app import __version__
from app.routers import galnet, health

app = FastAPI(
    title="ED-API",
    description="An API for Elite Dangerous 🌌.",
    version=__version__,
)

app.include_router(health.router)
app.include_router(galnet.router)
