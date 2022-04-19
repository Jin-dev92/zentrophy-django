# Generated by Django 4.0.4 on 2022-04-19 04:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import member.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('phone_number', models.CharField(max_length=12, null=True, unique=True)),
                ('address', models.CharField(blank=True, max_length=200)),
                ('address_detail', models.CharField(blank=True, max_length=200)),
                ('zipcode', models.CharField(blank=True, max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', member.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(default=None, null=True, verbose_name='삭제일')),
                ('card_number', models.CharField(max_length=16, null=True)),
                ('card_company', models.CharField(choices=[('bc', 'Bc'), ('kb', 'Kb'), ('samsung', 'Samsung'), ('shinhan', 'Shinhan'), ('uuri', 'Uuri'), ('hana', 'Hana'), ('lotte', 'Lotte'), ('hyundai', 'Hyundai'), ('nh', 'Nh'), ('etc', 'Etc')], default='etc', max_length=10)),
                ('validate_date', models.DateField(null=True)),
                ('security_code', models.CharField(max_length=4, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MemberOwnedVehicles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_created', models.DateTimeField(auto_now_add=True)),
                ('is_updated', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(default=None, null=True, verbose_name='삭제일')),
                ('license_code', models.CharField(default=None, max_length=50)),
                ('battery_left', models.IntegerField(default=-1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_created', models.DateTimeField(auto_now_add=True)),
                ('is_updated', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(default=None, null=True, verbose_name='삭제일')),
                ('name', models.CharField(max_length=100)),
                ('favorite', models.BooleanField(default=False)),
                ('card', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='member.card')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
