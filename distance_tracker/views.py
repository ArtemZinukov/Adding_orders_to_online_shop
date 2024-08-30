from django.shortcuts import render
from .models import Distance
from .utils import fetch_coordinates
from geopy.distance import geodesic
from django.http import JsonResponse
from environs import Env


env = Env()
env.read_env()

YANDEX_API_KEY = env('YANDEX_API_KEY')

def record_distance(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        restaurant_name = request.POST.get('restaurant_name')
        delivery_address = request.POST.get('delivery_address')

        restaurant_coords = fetch_coordinates(YANDEX_API_KEY, restaurant_name)
        delivery_coords = fetch_coordinates(YANDEX_API_KEY, delivery_address)

        if restaurant_coords and delivery_coords:
            distance_km = geodesic(restaurant_coords, delivery_coords).kilometers

            distance = Distance(order_id=order_id, restaurant_name=restaurant_name, distance_km=distance_km)
            distance.save()

            return JsonResponse({"status": "success", "message": "Distance recorded successfully."})
        else:
            return JsonResponse({"status": "error", "message": "Could not fetch coordinates."})

    return JsonResponse({"status": "error", "message": "Invalid request."})
