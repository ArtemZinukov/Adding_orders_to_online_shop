from django.contrib import admin
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.shortcuts import render

from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Order
from .models import OrderProduct


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 1


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'firstname', 'lastname', 'phonenumber', 'address', 'total_cost', 'status', 'get_restaurants'
    )
    search_fields = ('firstname', 'lastname', 'phonenumber')
    list_filter = ('status', 'accepted_at', 'processing_at', 'delivering_at', 'completed_at')
    inlines = [OrderProductInline]

    fieldsets = (
        (None, {
            'fields': (
                'firstname', 'lastname', 'phonenumber', 'address', 'total_cost', 'status', 'comment',
                'accepted_at', 'processing_at', 'delivering_at', 'completed_at'
            )
        }),
    )

    def get_restaurants(self, obj):
        restaurants = set()
        order_products = OrderProduct.objects.filter(order=obj)
        for order_product in order_products:
            menu_items = order_product.product.menu_items.filter(availability=True)
            for menu_item in menu_items:
                restaurants.add(menu_item.restaurant.name)
        return ", ".join(restaurants)

    get_restaurants.short_description = 'Рестораны'

    def response_change(self, request, obj):
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return super().response_change(request, obj)

    def save_model(self, request, obj, form, change):
        try:
            if obj.total_cost < 0:
                raise ValidationError("Стоимость заказа не может быть отрицательной.")
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, str(e), level='error')

