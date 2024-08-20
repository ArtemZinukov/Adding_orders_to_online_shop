import json

from django.http import JsonResponse
from django.templatetags.static import static
from django.shortcuts import get_object_or_404


from .models import Product, Order, OrderProduct


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


def register_order(request):
    try:
        order_data = json.loads(request.body.decode())
        order = Order(
            firstname=order_data['firstname'],
            lastname=order_data['lastname'],
            phonenumber=order_data['phonenumber'],
            address=order_data['address']
        )
        order.save()
        for profuct in order_data['products']:
            product_id = profuct['product']
            quantity = profuct['quantity']
            product = get_object_or_404(Product, id=product_id)
            order_product = OrderProduct(
                order=order,
                product=product,
                quantity=quantity
            )
            order_product.save()

        return JsonResponse({'message': 'Заказ успешно создан!', 'order_id': order.id}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
