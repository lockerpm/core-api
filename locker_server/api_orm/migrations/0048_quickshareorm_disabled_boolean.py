from django.db import migrations, models


def normalize_disabled(apps, schema_editor):
    """
    The `disabled` column was a float column. Normalize all non-zero values to 1 before changing it to a boolean
    column, so the database does not round the unexpected values (e.g. 0.4 => 0) while converting the column type
    """
    QuickShareORM = apps.get_model("api_orm", "QuickShareORM")
    QuickShareORM.objects.exclude(disabled=0).update(disabled=1)


class Migration(migrations.Migration):

    dependencies = [
        ('api_orm', '0047_teammemberorm_accepted_time'),
    ]

    operations = [
        migrations.RunPython(normalize_disabled, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='quickshareorm',
            name='disabled',
            field=models.BooleanField(default=False),
        ),
    ]
