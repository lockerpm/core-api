# Generated by Django 3.1.4 on 2021-10-06 04:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('cystack_models', '0004_userscore'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanType',
            fields=[
                ('name', models.CharField(max_length=128, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'cs_plan_types',
            },
        ),
        migrations.CreateModel(
            name='PMPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('alias', models.CharField(blank=True, default='', max_length=128)),
                ('name', models.CharField(max_length=128)),
                ('max_number', models.IntegerField(default=None, null=True)),
                ('max_device', models.IntegerField(default=None, null=True)),
                ('max_device_type', models.IntegerField(default=None, null=True)),
                ('price_usd', models.FloatField()),
                ('price_vnd', models.FloatField()),
                ('half_yearly_price_usd', models.FloatField(default=0)),
                ('half_yearly_price_vnd', models.FloatField(default=0)),
                ('yearly_price_usd', models.FloatField(default=0)),
                ('yearly_price_vnd', models.FloatField(default=0)),
                ('is_team_plan', models.BooleanField(default=False)),
                ('plan_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pm_plans', to='cystack_models.plantype')),
            ],
            options={
                'db_table': 'cs_pm_plans',
            },
        ),
        migrations.CreateModel(
            name='PromoCodeType',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'cs_promo_code_types',
            },
        ),
        migrations.AddField(
            model_name='collection',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='cipher',
            name='deleted_date',
            field=models.FloatField(null=True),
        ),
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=100, primary_key=True, serialize=False)),
                ('created_time', models.FloatField(null=True)),
                ('expired_time', models.FloatField()),
                ('remaining_times', models.IntegerField(default=0)),
                ('valid', models.BooleanField(default=True)),
                ('code', models.CharField(blank=True, max_length=100, null=True)),
                ('value', models.FloatField(default=0)),
                ('limit_value', models.FloatField(null=True)),
                ('duration', models.IntegerField(default=1)),
                ('specific_duration', models.CharField(default=None, max_length=128, null=True)),
                ('currency', models.CharField(default='USD', max_length=8)),
                ('description_en', models.TextField(blank=True, default='')),
                ('description_vi', models.TextField(blank=True, default='')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promo_codes', to='cystack_models.promocodetype')),
            ],
            options={
                'db_table': 'cs_promo_codes',
            },
        ),
        migrations.CreateModel(
            name='PMUserPlan',
            fields=[
                ('duration', models.CharField(default='monthly', max_length=128)),
                ('start_period', models.FloatField(default=None, null=True)),
                ('end_period', models.FloatField(default=None, null=True)),
                ('cancel_at_period_end', models.BooleanField(default=False)),
                ('custom_endtime', models.FloatField(default=None, null=True)),
                ('default_payment_method', models.CharField(default='wallet', max_length=128)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='pm_user_plan', serialize=False, to='cystack_models.user')),
                ('ref_plan_code', models.CharField(default=None, max_length=128, null=True)),
                ('number_members', models.IntegerField(default=1)),
                ('pm_stripe_subscription', models.CharField(max_length=255, null=True)),
                ('pm_stripe_subscription_created_time', models.IntegerField(null=True)),
                ('pm_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pm_user_plan', to='cystack_models.pmplan')),
                ('promo_code', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pm_user_plans', to='cystack_models.promocode')),
            ],
            options={
                'db_table': 'cs_pm_user_plan',
            },
        ),
        migrations.CreateModel(
            name='CipherFolder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cipher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ciphers_folders', to='cystack_models.cipher')),
                ('folder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ciphers_folders', to='cystack_models.folder')),
            ],
            options={
                'db_table': 'cs_ciphers_folders',
                'unique_together': {('cipher', 'folder')},
            },
        ),
    ]
