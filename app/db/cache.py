from redis import Redis
from app.config import Config

r = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0)


async def set_seen_vacancies(user_telegram_id, vacancies):
    r.sadd(user_telegram_id, *vacancies)


async def get_seen_vacancies(user_telegram_id):
    vacancies = r.smembers(user_telegram_id)
    if not vacancies:
        return set()
    return vacancies
