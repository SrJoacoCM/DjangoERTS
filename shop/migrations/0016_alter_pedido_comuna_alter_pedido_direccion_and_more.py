# Generated by Django 5.0.6 on 2024-07-04 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0015_pedido_comuna_pedido_direccion_pedido_region_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='comuna',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='pedido',
            name='direccion',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='pedido',
            name='region',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='pedido',
            name='telefono',
            field=models.CharField(max_length=20),
        ),
    ]
