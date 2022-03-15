# Generated by Django 4.0.2 on 2022-03-15 05:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
        ('order', '0003_orderdetail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdetail',
            name='product',
        ),
        migrations.RemoveField(
            model_name='orderdetail',
            name='vehicle',
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='product_options',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.productoptions'),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='vehicle_color',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.vehiclecolor'),
        ),
    ]