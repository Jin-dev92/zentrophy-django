# Generated by Django 4.0.4 on 2022-04-19 04:15

from django.db import migrations, models

import history.constant


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AfterService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_created', models.DateTimeField(auto_now_add=True)),
                ('is_updated', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(default=None, null=True, verbose_name='삭제일')),
                ('registration_number', models.CharField(max_length=16, unique=True)),
                ('status', models.PositiveSmallIntegerField(default=history.constant.AfterServiceStatus['APPLY_WAITING'])),
                ('reservation_date', models.DateTimeField(null=True)),
                ('detail', models.TextField(blank=True)),
                ('category', models.PositiveSmallIntegerField(default=history.constant.AfterServiceCategory['ETC'])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BatteryExchange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_created', models.DateTimeField(auto_now_add=True)),
                ('is_updated', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(default=None, null=True, verbose_name='삭제일')),
                ('used_battery', models.FloatField(default=0.0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_created', models.DateTimeField(auto_now_add=True)),
                ('is_updated', models.DateTimeField(auto_now=True)),
                ('amount', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_created', models.DateTimeField(auto_now_add=True)),
                ('is_updated', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(default=None, null=True, verbose_name='삭제일')),
                ('reject_reason', models.CharField(blank=True, max_length=200)),
                ('method', models.PositiveSmallIntegerField(default=history.constant.RefundMethod['RECALL_REQUEST'])),
                ('status', models.PositiveSmallIntegerField(default=history.constant.RefundStatus['WAITING'])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Warranty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_created', models.DateTimeField(auto_now_add=True)),
                ('is_updated', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(default=None, null=True, verbose_name='삭제일')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('validity', models.DateTimeField(null=True)),
                ('is_warranty', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
