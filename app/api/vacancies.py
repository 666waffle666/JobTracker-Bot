import httpx
from . import BASE_URL


async def get_vacancies_data(query_params):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/vacancies", params=query_params)
        resp.raise_for_status()
        data = resp.json()
        return data
