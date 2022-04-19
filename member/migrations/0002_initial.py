# Generated by Django 4.0.4 on 2022-04-19 04:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
        ('product', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('member', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberownedvehicles',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.order'),
        ),
        migrations.AddField(
            model_name='memberownedvehicles',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='memberownedvehicles',
            name='vehicle',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.vehicle'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.group'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
