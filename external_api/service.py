import httpx
import asyncio

from pydantic import HttpUrl

from . import config
from . import models


class CatApiService:
    def __init__(self):
        # create client
        self.client = httpx.AsyncClient()

    async def __aenter__(self):
        # open connection with "async with"
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # close connection
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def _get_neko(self) -> (models.WaifuPicResponse | None, int):
        """
        Get Neko and status code for http cat
        """

        try:
            response = await self.client.get(config.WAIFU_PICS_API_URL)
            status_code = response.status_code

            if status_code == 200:
                # DTO
                data = models.WaifuPicResponse(**response.json())
                return data, status_code

            # return none and error status code
            return None, status_code

        except Exception:
            return None, 503

    async def _get_fact(self) -> models.MeowFactResponse | None:
        """
        Cat fact
        """

        try:
            response = await self.client.get(config.MEOWFACTS_API_URL)
            response.raise_for_status()
            return models.MeowFactResponse(**response.json())
        except Exception:
            return None

    async def get_dashboard_data(self) -> models.DashboardResponseModel:
        """
        Get all data and set in biiiig DTO
        """
        neko_task = self._get_neko()
        fact_task = self._get_fact()

        (neko_data, neko_status), fact_data = await asyncio.gather(
            neko_task, fact_task
        )

        if neko_data:
            neko_url = neko_data.url
        else:
            # if waifu.pics is down, return car 503
            neko_url = f"{config.HTTP_CAT_BASE_URL}/503"

        # get neko status for http car
        http_cat_url = f"{config.HTTP_CAT_BASE_URL}/{neko_status}"

        # get cat fact
        if fact_data and fact_data.data:
            fact_text = fact_data.data[0]
        else:
            fact_text = "Не вдалося завантажити факт про кота. (API meowfacts недоступний)"

        # return biiig DTO
        return models.DashboardResponseModel(
            neko_image_url=neko_url,
            fact=fact_text,
            http_cat_url= HttpUrl(http_cat_url)
        )