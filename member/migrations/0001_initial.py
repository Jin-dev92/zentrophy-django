# Generated by Django 4.0.1 on 2022-02-05 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('is_created', models.DateTimeField(auto_now_add=True)),
                ('is_updated', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('address', models.CharField(blank=True, max_length=200)),
                ('address_detail', models.CharField(blank=True, max_length=200)),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('zipCode', models.CharField(blank=True, max_length=20)),
                ('is_business', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]