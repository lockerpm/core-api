# Generated by Django 3.2.23 on 2024-03-14 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_orm', '0021_auto_20240312_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentorm',
            name='saas_market',
            field=models.CharField(db_index=True, default=None, max_length=128, null=True),
        ),
    ]
