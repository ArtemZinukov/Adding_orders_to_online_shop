# Generated by Django 3.2.15 on 2024-08-27 15:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_alter_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='accepted_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата и время принятия'),
        ),
        migrations.AddField(
            model_name='order',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата и время выполнения'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivering_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата и время доставки'),
        ),
        migrations.AddField(
            model_name='order',
            name='processing_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата и время сборки'),
        ),
    ]
