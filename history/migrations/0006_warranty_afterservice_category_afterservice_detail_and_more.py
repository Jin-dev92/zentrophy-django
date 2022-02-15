# Generated by Django 4.0.2 on 2022-02-15 14:42

from django.db import migrations, models
import history.constant


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0005_remove_refund_reject_method_refund_method'),
    ]

    operations = [
        migrations.CreateModel(
            name='Warranty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_created', models.DateTimeField(auto_now_add=True)),
                ('is_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('validity', models.DateTimeField(null=True)),
                ('is_warranty', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='afterservice',
            name='category',
            field=models.PositiveSmallIntegerField(default=history.constant.AfterServiceCategory['ETC']),
        ),
        migrations.AddField(
            model_name='afterservice',
            name='detail',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='afterservice',
            name='reservation_date',
            field=models.DateTimeField(null=True),
        ),
    ]
