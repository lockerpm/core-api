# Generated by Django 3.1.4 on 2022-11-14 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cystack_models', '0079_auto_20221114_1102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
