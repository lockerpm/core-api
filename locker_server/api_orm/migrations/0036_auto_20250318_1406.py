# Generated by Django 3.2.23 on 2025-03-18 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_orm', '0035_auto_20250212_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='deviceorm',
            name='h',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='deviceorm',
            name='p',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
