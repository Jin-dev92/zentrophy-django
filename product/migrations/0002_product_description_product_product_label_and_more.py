# Generated by Django 4.0.1 on 2022-01-17 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='product_label',
            field=models.IntegerField(choices=[(0, 'Hot'), (1, 'New'), (2, 'Sale'), (3, 'Best')], default=1),
        ),
        migrations.AddField(
            model_name='product',
            name='product_options',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='display_line',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
