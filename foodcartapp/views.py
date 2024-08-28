import json
from itertools import product
from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static

from rest_framework.decorators import api_view
from rest_framework import status

from rest_framework.response import Response

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import CharField, ListField
from rest_framework.exceptions import ValidationError
from .models import Product, Order, OrderProduct, Restaurant, RestaurantMenuItem


class OrderProductSerializer(ModelSerializer):
    product = CharField()

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ListField(child=OrderProductSerializer(), write_only=True)

    class Meta:
        model = Order
        fields = ['id','firstname', 'lastname', 'phonenumber', 'address', 'products']

    def validate_products(self, value):
        if not value :
            raise ValidationError('Список продуктов не может быть пустым')
        return value


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address'],
    )

    all_restaurants = None

    for product in serializer.validated_data['products']:
        product_instance = Product.objects.get(id=product['product'])

        OrderProduct.objects.create(
            order=order,
            product=product_instance,
            quantity=product['quantity']
        )

        product_restaurants = set(
            RestaurantMenuItem.objects.filter(product=product_instance, availability=True).values_list(
                'restaurant__name', flat=True))

        if all_restaurants is None:
            all_restaurants = product_restaurants
        else:
            all_restaurants = all_restaurants.intersection(product_restaurants)

    order.calculate_total_cost()
    order_data = OrderSerializer(order).data

    return Response({"order": order_data, "restaurants": list(all_restaurants)}, status=status.HTTP_201_CREATED)
