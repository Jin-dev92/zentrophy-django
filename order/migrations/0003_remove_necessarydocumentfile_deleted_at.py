# Generated by Django 4.0.4 on 2022-04-26 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_rename_is_able_subside_order_is_visited_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='necessarydocumentfile',
            name='deleted_at',
        ),
    ]
