from redis.asyncio import from_url
from app.config import Config
from datetime import datetime, timezone, timedelta

r = from_url(
    url=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}", decode_responses=True
)


async def set_last_check(telegram_id):
    timestamp = datetime.now(timezone.utc).isoformat()
    return await r.set(
        f"user:{telegram_id}:last_check", value=str(timestamp), ex=86400
    )  # TTL = 1 day


async def get_last_check(telegram_id):
    last_check = (
        await r.get(f"user:{telegram_id}:last_check")
        or (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    )
    if isinstance(last_check, str):
        last_check = datetime.fromisoformat(last_check).astimezone(timezone.utc)

    print(await r.get(f"user:{telegram_id}:last_check"))
    return last_check
