# Generated by Django 4.0.2 on 2022-02-17 05:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_alter_productimage_product_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productoptions',
            old_name='product',
            new_name='product_id',
        ),
    ]