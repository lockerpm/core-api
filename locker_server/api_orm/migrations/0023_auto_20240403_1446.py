# Generated by Django 3.2.23 on 2024-04-03 07:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api_orm', '0022_auto_20240314_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentorm',
            name='channel',
            field=models.CharField(default='organic', max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='paymentorm',
            name='net_price',
            field=models.FloatField(default=0),
        )
    ]
