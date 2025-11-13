import httpx
from . import BASE_URL


async def get_area_id(city: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/areas")
        resp.raise_for_status()
        areas = resp.json()

        def search_area(areas):
            for area in areas:
                if area["name"].lower() == city.lower():
                    return area["id"]
                # рекурсивный поиск внутри
                result = search_area(area["areas"])
                if result:
                    return result
            return None

    return search_area(areas)
