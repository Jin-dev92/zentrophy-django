# Generated by Django 4.0.3 on 2022-04-01 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_alter_vehicleimage_vehicle_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='productdisplayline',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='productimage',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='productoptions',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='vehiclecolor',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='vehicleimage',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
    ]