import requests
from .models import Location


def fetch_coordinates(apikey, address):
    location, created = Location.objects.get_or_create(address=address)

    # Если данные устарели, обновляем их
    if location.needs_update():
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")

        # Обновляем координаты и дату последнего обновления
        location.latitude = float(lat)
        location.longitude = float(lon)
        location.save()

    return location.latitude, location.longitude  # Возвращаем (широта, долгота)
