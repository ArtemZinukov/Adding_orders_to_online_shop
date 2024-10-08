# Generated by Django 3.2.15 on 2024-08-26 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_order_total_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('accepted', 'Заказ принят'), ('processing', 'Заказ собирается'), ('delivering', 'Заказ доставляется'), ('completed', 'Выполнен')], default='new', max_length=20, verbose_name='Статус заказа'),
        ),
    ]
