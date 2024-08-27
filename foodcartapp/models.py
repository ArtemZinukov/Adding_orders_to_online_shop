from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('accepted', 'Заказ принят'),
        ('processing', 'Заказ собирается'),
        ('delivering', 'Заказ доставляется'),
        ('completed', 'Выполнен'),
    )

    PAYMENT_CHOICES = (
        ('cash', 'Наличные'),
        ('card', 'Банковская карта'),
        ('online', 'Онлайн-оплата'),
    )

    firstname = models.CharField(max_length=50, verbose_name="Имя")
    lastname = models.CharField(max_length=50, verbose_name="Фамилия")
    phonenumber = PhoneNumberField(verbose_name="Номер телефона")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    products = models.ManyToManyField(Product, through='OrderProduct', verbose_name="Товары")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость заказа", default=0)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='accepted', verbose_name="Статус заказа")
    comment = models.TextField(blank=True, null=True, default='', verbose_name="Комментарий")
    accepted_at = models.DateTimeField(default=timezone.now, verbose_name="Дата и время принятия")
    processing_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата и время сборки")
    delivering_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата и время доставки")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата и время выполнения")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash',
                                      verbose_name="Способ оплаты")

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.firstname} {self.lastname} - Заказ {self.id}"

    def calculate_total_cost(self):
        total = sum(item.product.price * item.quantity for item in self.orderproduct_set.all())
        self.total_cost = round(total, 2)
        self.save()

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        unique_together = ('order', 'product')
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
