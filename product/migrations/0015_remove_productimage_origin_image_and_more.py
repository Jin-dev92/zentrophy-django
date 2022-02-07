# Generated by Django 4.0.1 on 2022-02-03 04:06

from django.db import migrations, models
import django.db.models.deletion
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0014_alter_productimage_origin_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productimage',
            name='origin_image',
        ),
        migrations.RemoveField(
            model_name='productimage',
            name='product_options',
        ),
        migrations.RemoveField(
            model_name='vehicleimage',
            name='origin_image',
        ),
        migrations.AddField(
            model_name='productimage',
            name='thumb-product121278856358952',
            field=sorl.thumbnail.fields.ImageField(null=True, upload_to='thumb/%Y/%M'),
        ),
        migrations.AddField(
            model_name='vehicleimage',
            name='thumb-vehicle1778947343881',
            field=sorl.thumbnail.fields.ImageField(null=True, upload_to='thumb/%Y/%M'),
        ),
        migrations.AlterField(
            model_name='vehicleimage',
            name='vehicle',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.vehicle'),
        ),
    ]