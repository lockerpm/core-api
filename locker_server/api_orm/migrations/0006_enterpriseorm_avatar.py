# Generated by Django 3.2.20 on 2023-10-25 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_orm', '0005_auto_20231020_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='enterpriseorm',
            name='avatar',
            field=models.ImageField(default=None, null=True, upload_to='avatars/'),
        ),
    ]
