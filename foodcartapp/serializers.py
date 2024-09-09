from rest_framework import serializers
from .models import Order, OrderProduct, Product

class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.CharField()

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError('Список продуктов не может быть пустым')
        return value

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        for product in products:
            product_instance = Product.objects.get(id=product['product'])
            OrderProduct.objects.create(
                order=order,
                product=product_instance,
                quantity=product['quantity']
            )

        order.calculate_total_cost()
        return order
