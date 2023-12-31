# Generated by Django 3.2.20 on 2023-10-13 04:14
import json
import os

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid

from locker_server.shared.constants.sso_provider import LIST_VALID_SSO_PROVIDERS

FIXTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
FIXTURE_FILENAMES = ['sso_providers.json']


def get_swappable_model(fixture_filename):
    from locker_server.api_orm.models import SSOProviderORM
    return SSOProviderORM


def load_fixtures(apps, schema_editor):
    for fixture_filename in FIXTURE_FILENAMES:
        fixture_file = os.path.join(FIXTURE_DIR, fixture_filename)
        fixture = open(fixture_file, 'rb')
        data = json.loads(fixture.read())
        model_orm = get_swappable_model(fixture_filename=fixture_filename)
        if not model_orm:
            continue
        objs = []
        for d in data:
            objs.append(model_orm(**d.get("fields")))

        results = model_orm.objects.bulk_create(objs, ignore_conflicts=True, batch_size=100)
        print(f"[+] Done load {len(results)} objects from {fixture_filename}")


def unload_fixtures(apps, schema_editor):
    """ Brutally deleting all entries for this model... """

    for fixture_filename in FIXTURE_FILENAMES:
        model_orm = get_swappable_model(fixture_filename=fixture_filename)
        if not model_orm:
            continue
        model_orm.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('api_orm', '0003_auto_20231010_1609'),
    ]

    operations = [
        migrations.CreateModel(
            name='SSOProviderORM',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('order_index', models.IntegerField(db_index=True)),
            ],
            options={
                'db_table': 'cs_sso_providers',
            },
        ),
        migrations.CreateModel(
            name='SSOConfigurationORM',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=128, primary_key=True, serialize=False)),
                ('identifier', models.CharField(db_index=True, max_length=255, unique=True)),
                ('sso_provider_options', models.CharField(max_length=10244, blank=True, default='', null=True)),
                ('enabled', models.BooleanField(default=False, null=True)),
                ('creation_date', models.FloatField()),
                ('revision_date', models.FloatField(null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                 related_name='created_sso_configurations', to=settings.LS_USER_MODEL)),
                ('sso_provider',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sso_configurations',
                                   to='api_orm.ssoproviderorm')),
            ],
            options={
                'db_table': 'cs_sso_configurations',
                'abstract': False,
                'swappable': 'LS_SSO_CONFIGURATION_MODEL',
            },
        ),
        # Load data from fixtures
        migrations.RunPython(load_fixtures, reverse_code=unload_fixtures),
    ]
