# Generated by Django 3.1.4 on 2022-03-10 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cystack_models', '0039_auto_20220309_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pmuserplan',
            name='pm_mobile_subscription',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
