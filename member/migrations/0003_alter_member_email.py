# Generated by Django 4.0.1 on 2022-02-05 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0002_remove_member_is_created_remove_member_is_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='email',
            field=models.EmailField(max_length=100),
        ),
    ]
