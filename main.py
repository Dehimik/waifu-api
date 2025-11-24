from fastapi import FastAPI
from contextlib import asynccontextmanager
from external_api import router as cat_router
from database.base import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Cat Dashboard API",
    version="2.1.0",
    lifespan=lifespan
)

app.include_router(cat_router.router, prefix="/api", tags=["Cat Dashboard"])

@app.get("/")
def read_root():
    return {"message": "Go to /api/dashboard/view"}