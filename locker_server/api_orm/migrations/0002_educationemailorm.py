# Generated by Django 3.2.20 on 2023-10-02 07:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_orm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationEmailORM',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.FloatField()),
                ('email', models.EmailField(db_index=True, max_length=255)),
                ('education_type', models.CharField(default='student', max_length=64)),
                ('university', models.CharField(blank=True, max_length=255)),
                ('verified', models.BooleanField(default=False)),
                ('verification_token', models.CharField(max_length=512, null=True)),
                ('promo_code', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education_emails', to=settings.LS_USER_MODEL)),
            ],
            options={
                'db_table': 'cs_education_email',
                'unique_together': {('user', 'email')},
            },
        ),
    ]
