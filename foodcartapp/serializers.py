from rest_framework import serializers
from .models import Order, OrderProduct

class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.CharField()

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.ListField(child=OrderProductSerializer(), required=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']
