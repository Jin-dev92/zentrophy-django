# Generated by Django 4.0.1 on 2022-01-24 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=200)),
                ('user_mail', models.EmailField(max_length=200, unique=True)),
                ('phone_number', models.CharField(max_length=12)),
                ('address', models.CharField(max_length=200)),
            ],
        ),
    ]
