# Generated by Django 4.0.3 on 2022-04-01 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0003_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='afterservice',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='batteryexchange',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='refund',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='warranty',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
    ]