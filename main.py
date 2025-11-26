from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.base import init_db
from external_api import router as cat_router
from logs.logger_config import setup_logging
from logs.sentry import init_sentry


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    init_sentry()

    await init_db()
    yield


app = FastAPI(title="Cat Dashboard API", version="2.1.0", lifespan=lifespan)

app.include_router(cat_router.router, prefix="/api", tags=["Cat Dashboard"])


@app.get("/")
def read_root():
    return {"message": "Go to /api/dashboard/view"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
