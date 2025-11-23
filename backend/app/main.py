from typing import AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from logging import INFO, basicConfig, getLogger

from app.db.engine import init_db
from app.api.v1.router import api_router

logger = getLogger(__name__)
basicConfig(level=INFO)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up...")
    await init_db()
    yield
    logger.info("Shutting down..")
    logger.info("Fiinished.")

def get_app() -> FastAPI:
    app = FastAPI(title="SyncUs API", lifespan=lifespan)
    app.include_router(api_router, prefix="/api/v1")
    return app

app = get_app()

@app.get("/")
async def root():
    return {"message": "SyncUs API"}