# Generated by Django 4.0.1 on 2022-01-26 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('placement', '0002_alter_placement_operation_end_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placement',
            name='operation_end',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='placement',
            name='operation_start',
            field=models.DateField(),
        ),
    ]