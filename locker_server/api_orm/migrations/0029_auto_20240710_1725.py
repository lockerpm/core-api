# Generated by Django 3.2.23 on 2024-07-10 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_orm', '0028_auto_20240705_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backupcredentialorm',
            name='fd_credential_id',
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='userorm',
            name='fd_credential_id',
            field=models.CharField(max_length=300, null=True),
        ),
    ]
