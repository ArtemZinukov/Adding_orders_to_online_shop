from rest_framework import serializers
from .models import Order, OrderProduct, Product
from distance_tracker.models import Distance
from geopy.distance import geodesic
from distance_tracker.utils import fetch_coordinates
from environs import Env

env = Env()
env.read_env()

YANDEX_API_KEY = env('YANDEX_API_KEY')


class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        for product in products:
            product_instance = product['product']
            OrderProduct.objects.create(
                order=order,
                product=product_instance,
                quantity=product['quantity']
            )

            distance_record, created = Distance.objects.get_or_create(
                order=order,
                restaurant_name=product_instance.restaurant.name,
                defaults={'distance_km': 0.0}
            )

            try:
                restaurant_coords = fetch_coordinates(YANDEX_API_KEY, product_instance.restaurant.name)
                delivery_coords = fetch_coordinates(YANDEX_API_KEY, order.address)

                if restaurant_coords and delivery_coords:
                    distance = geodesic(restaurant_coords, delivery_coords).kilometers
                    distance_record.distance_km = distance
                    distance_record.save()
            except Exception as e:
                print(f"Ошибка при получении координат для {product_instance.restaurant.name}: {e}")

        order.calculate_total_cost()
        return order
