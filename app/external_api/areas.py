from app.db.cache import load_areas

city_map = {}


def build_city_map(areas):
    def walk(areas):
        for area in areas:
            city_map[area["name"].lower()] = area["id"]
            walk(area["areas"])

    walk(areas)


async def get_area_id(city: str):
    global city_map

    if not city_map:
        areas = await load_areas()
        build_city_map(areas)

    return city_map.get(city.lower())
