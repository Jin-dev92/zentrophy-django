# Generated by Django 4.0.1 on 2022-02-07 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0017_alter_productimage_origin_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_display_line',
            field=models.ManyToManyField(to='product.ProductDisplayLine'),
        ),
    ]
