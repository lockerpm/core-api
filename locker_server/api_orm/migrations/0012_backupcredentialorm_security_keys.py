# Generated by Django 3.2.22 on 2023-11-28 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_orm', '0011_auto_20231127_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='backupcredentialorm',
            name='security_keys',
            field=models.TextField(default=None, null=True),
        ),
    ]