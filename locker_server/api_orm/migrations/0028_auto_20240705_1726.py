# Generated by Django 3.2.23 on 2024-07-05 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_orm', '0027_auto_20240704_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='cipherorm',
            name='password_history',
            field=models.TextField(blank=True, default='', null=True),
        )
    ]