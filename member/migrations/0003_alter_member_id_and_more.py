# Generated by Django 4.0.2 on 2022-02-12 10:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0003_afterservice_owner'),
        ('product', '0001_initial'),
        ('order', '0002_order_is_vehicle_alter_order_owner'),
        ('member', '0002_alter_member_id_memberownedvehicles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='memberownedvehicles',
            name='battery_left',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='memberownedvehicles',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='memberownedvehicles',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.order'),
        ),
        migrations.AlterField(
            model_name='memberownedvehicles',
            name='recent_exchange_history',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='history.batteryexchange'),
        ),
        migrations.AlterField(
            model_name='memberownedvehicles',
            name='vehicle',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.vehicle'),
        ),
    ]