# Generated by Django 4.0.1 on 2022-01-20 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_rename_vehiclecolormodel_vehiclecolor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.JSONField(default={}),
        ),
    ]
