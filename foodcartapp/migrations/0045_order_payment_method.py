# Generated by Django 3.2.15 on 2024-08-27 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_auto_20240827_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'Наличные'), ('card', 'Банковская карта'), ('online', 'Онлайн-оплата')], default='cash', max_length=20, verbose_name='Способ оплаты'),
        ),
    ]
