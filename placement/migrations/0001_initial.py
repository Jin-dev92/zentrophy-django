# Generated by Django 4.0.1 on 2022-01-19 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Placement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('placement_name', models.CharField(blank=True, max_length=100)),
                ('placement_owner', models.CharField(blank=True, max_length=20)),
                ('placement_address', models.CharField(blank=True, max_length=100)),
                ('placement_type', models.PositiveSmallIntegerField(choices=[(0, 'Service'), (1, 'Direct'), (2, 'Exchange')], default=0)),
                ('operation_start', models.CharField(blank=True, max_length=10)),
                ('operation_end', models.CharField(blank=True, max_length=10)),
                ('operation_state', models.PositiveSmallIntegerField(choices=[(0, 'Operating'), (1, 'Constructing'), (2, 'Soon')], default=0)),
            ],
        ),
    ]
