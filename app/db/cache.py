from redis.asyncio import from_url
from app.config import Config
from datetime import datetime, timezone, timedelta
import httpx
import json

BASE_URL = "https://api.hh.ru"

city_map = {}  # память процесса, быстрый доступ
CACHE_EXPIRE = 86400  # TTL = 1 day

r = from_url(
    url=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}", decode_responses=True
)


# vacancies
async def set_last_check(telegram_id):
    timestamp = datetime.now(timezone.utc).isoformat()
    return await r.set(
        f"user:{telegram_id}:last_check", value=str(timestamp), ex=CACHE_EXPIRE
    )


async def get_last_check(telegram_id):
    last_check = (
        await r.get(f"user:{telegram_id}:last_check")
        or (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    )
    if isinstance(last_check, str):
        last_check = datetime.fromisoformat(last_check).astimezone(timezone.utc)

    print(await r.get(f"user:{telegram_id}:last_check"))
    return last_check


# areas
async def load_areas():
    cached = await r.get("hh_areas")
    if cached:
        return json.loads(cached)

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/areas")
        resp.raise_for_status()
        areas = resp.json()

    await r.set("hh_areas", json.dumps(areas), ex=CACHE_EXPIRE)
    return areas
