# Generated by Django 4.0.1 on 2022-01-20 07:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_delete_vehiclesubsidy_remove_vehicle_extra_subsidy_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productdisplayline',
            name='product_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
    ]