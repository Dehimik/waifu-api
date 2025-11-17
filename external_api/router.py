from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from . import models
from .service import CatApiService

router = APIRouter()

async def get_api_service():
    async with CatApiService() as service:
        yield service

@router.get(
    "/dashboard/view",
    response_class=HTMLResponse,
    summary="Show dashboard",
    description="Get neko, fact, and status car and render to html"
)
async def get_dashboard_view(
        service: CatApiService = Depends(get_api_service)
):
    data = await service.get_dashboard_data()

    # Get status for status car
    status_code = data.http_cat_url.path.split('/')[-1]

    # create html
    html_content = f"""
    <html>
    <head>
        <title>Cat Dashboard</title>
    </head>
    <body>
        <div class="container">
            <h1>Neko Image</h1>
            <img src="{data.neko_image_url}" alt="Neko Image">

            <h2>Cat Fact</h2>
            <p class="fact">{data.fact}</p>

            <h2>Status Cat: {status_code}</h2>
            <img src="{data.http_cat_url}" alt="HTTP Status Cat">
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get(
    "/dashboard/json",
    response_model=models.DashboardResponseModel,
    summary="Get dashboard data in json",
    description="Отримує Neko, факт, та кіт-статус у чистому JSON-форматі."
)
async def get_dashboard_json(
        service: CatApiService = Depends(get_api_service)
):
    """
    Цей ендпоїнт повертає чисті дані.
    Він автоматично валідує відповідь за 'DashboardResponseModel'
    і генерує документацію Swagger.
    """
    return await service.get_dashboard_data()