# Generated by Django 4.0.4 on 2022-04-26 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='is_able_subside',
            new_name='is_visited',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_info',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_type',
        ),
        migrations.AddField(
            model_name='order',
            name='buy_list',
            field=models.JSONField(default=dict, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='extra_subside',
            field=models.ManyToManyField(to='order.extrasubside'),
        ),
        migrations.AddField(
            model_name='order',
            name='subside',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
