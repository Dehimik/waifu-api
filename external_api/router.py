from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
from .service import CatApiService
from database.utils import get_db

router = APIRouter()

async def get_api_service(db: AsyncSession = Depends(get_db)):
    async with CatApiService(db) as service:
        yield service

@router.get("/dashboard/view", response_class=HTMLResponse)
async def get_dashboard_view(
    bg_tasks: BackgroundTasks,
    service: CatApiService = Depends(get_api_service)
):
    data = await service.get_dashboard_data(bg_tasks)
    status_code = str(data.http_cat_url).split('/')[-1]

    html_content = f"""
    <html>
    <head><title>Cat Dashboard</title></head>
    <body style="font-family: sans-serif; text-align: center; background: #222; color: #fff;">
        <h1>Neko Dashboard</h1>
        <img src="{data.neko_image_url}" style="max-height: 400px; border-radius: 10px;">
        <h3>Random Fact:</h3>
        <p style="font-style: italic; color: #ffa;">{data.fact}</p>
        <h4>Status Code: {status_code}</h4>
        <img src="{data.http_cat_url}" width="100" style="border-radius: 5px;">
        <br><br><hr>
        <a href="/api/history" style="color: #4af;">View Local History (DB)</a>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/dashboard/json", response_model=models.DashboardResponseModel)
async def get_dashboard_json(
    bg_tasks: BackgroundTasks,
    service: CatApiService = Depends(get_api_service)
):
    return await service.get_dashboard_data(bg_tasks)

@router.get("/history")
async def get_history(
    limit: int = 10,
    service: CatApiService = Depends(get_api_service)
):
    return await service.get_history(limit)