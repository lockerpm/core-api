# Generated by Django 3.2.22 on 2023-12-06 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_orm', '0013_auto_20231129_1017'),
    ]

    operations = [
        migrations.AddField(
            model_name='userorm',
            name='fd_name',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]