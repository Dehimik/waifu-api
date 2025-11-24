import httpx
import asyncio
import json
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from . import config
from . import models
from settings import settings
from database.base_schema import CatLog


class CatApiService:
    def __init__(self, db: AsyncSession):
        self.client = httpx.AsyncClient()
        self.db = db

        self.redis = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            ssl_cert_reqs="none"  # Important for Upstash
        )

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)
        await self.redis.close()

    async def _get_neko(self):
        try:
            resp = await self.client.get(config.WAIFU_PICS_API_URL)
            return (models.WaifuPicResponse(**resp.json()), resp.status_code) if resp.status_code == 200 else (None,
                                                                                                               resp.status_code)
        except:
            return None, 503

    async def _get_fact(self):
        try:
            resp = await self.client.get(config.MEOWFACTS_API_URL)
            return models.MeowFactResponse(**resp.json())
        except:
            return None

    async def _fetch_from_api(self) -> models.DashboardResponseModel:
        neko_task = self._get_neko()
        fact_task = self._get_fact()
        (neko_data, neko_status), fact_data = await asyncio.gather(neko_task, fact_task)

        neko_url = neko_data.url if neko_data else f"{config.HTTP_CAT_BASE_URL}/503"
        http_cat_url = f"{config.HTTP_CAT_BASE_URL}/{neko_status}"
        fact_text = fact_data.data[0] if (fact_data and fact_data.data) else "Meow API down."

        return models.DashboardResponseModel(
            neko_image_url=neko_url,
            fact=fact_text,
            http_cat_url=http_cat_url
        )

    async def _save_to_db(self, data: models.DashboardResponseModel):
        new_entry = CatLog(
            fact=data.fact,
            neko_url=str(data.neko_image_url),
            http_cat_status=str(data.http_cat_url).split('/')[-1]
        )
        self.db.add(new_entry)
        await self.db.commit()

    async def refill_queue(self, count: int = 5):
        print(f"Background: Refilling queue (+{count})...")
        for _ in range(count):
            try:
                data = await self._fetch_from_api()
                await self._save_to_db(data)
                await self.redis.rpush(settings.redis_queue_key, data.model_dump_json())
            except Exception as e:
                print(f"Error filling queue: {e}")

    async def get_dashboard_data(self, background_tasks) -> models.DashboardResponseModel:
        # Try get from redis
        try:
            cached_json = await self.redis.lpop(settings.redis_queue_key)
            queue_len = await self.redis.llen(settings.redis_queue_key)
        except Exception as e:
            # If Redis (Upstash) is down work without cash
            print(f"Redis Error: {e}")
            cached_json = None
            queue_len = 0

        # Check for queue length and refill if need
        if queue_len < settings.redis_min_size:
            background_tasks.add_task(self.refill_queue, count=3)

        if cached_json:
            print("Cache Hit: Served from Redis")
            return models.DashboardResponseModel(**json.loads(cached_json))

        print("Cache Miss: Direct Fetch")
        data = await self._fetch_from_api()
        await self._save_to_db(data)
        return data

    async def get_history(self, limit: int = 10):
        stmt = select(CatLog).order_by(CatLog.created_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()