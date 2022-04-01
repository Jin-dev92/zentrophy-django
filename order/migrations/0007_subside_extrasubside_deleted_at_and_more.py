# Generated by Django 4.0.3 on 2022-04-01 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_remove_order_is_deleted_order_deleted_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subside',
            fields=[
                ('deleted_at', models.DateTimeField(default=None, null=True, verbose_name='삭제일')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='extrasubside',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='integratedfeeplan',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='necessarydocumentfile',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
    ]
