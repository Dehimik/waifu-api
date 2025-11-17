from fastapi import FastAPI
from external_api import router as cat_router  # Імпортуємо наш роутер

app = FastAPI(
    title="Cat Dashboard API",
    description="API for 3 APIs HELL YEAHHHH.",
    version="1.0.0"
)

app.include_router(cat_router.router, prefix="/api", tags=["Cat Dashboard"])

@app.get("/", summary="Root Endpoint", include_in_schema=False)
def read_root():
    """
    Check if work
    """
    return {
        "message": "Welcome to the Cat Dashboard API. "
                   "Go to /api/dashboard/view to see the dashboard, "
                   "or /docs for API documentation."
    }