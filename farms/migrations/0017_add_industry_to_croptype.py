# Generated manually - Add industry field to CropType model
# Idempotent: adds industry_id only if missing (avoids DuplicateColumn on existing DBs)

from django.db import migrations, models
import django.db.models.deletion


def safe_add_industry_and_assign(apps, schema_editor):
    """Add industry_id column if missing, then assign default industry to CropTypes."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'farms_croptype' AND column_name = 'industry_id'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE farms_croptype
                ADD COLUMN industry_id BIGINT NULL
                REFERENCES users_industry(id) ON DELETE CASCADE
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS farms_croptype_industry_id_idx
                ON farms_croptype(industry_id)
            """)

    Industry = apps.get_model('users', 'Industry')
    CropType = apps.get_model('farms', 'CropType')

    try:
        default_industry = Industry.objects.first()
        if not default_industry:
            print("⚠️  No industry found. Creating default industry...")
            default_industry = Industry.objects.create(
                name='Default Industry',
                description='Default industry for existing crop types'
            )
            print(f"✅ Created default industry: {default_industry.name}")
        else:
            print(f"ℹ️  Using existing industry: {default_industry.name}")
    except Exception as e:
        print(f"⚠️  Error getting industry: {e}")
        return

    crop_types_updated = CropType.objects.filter(industry__isnull=True).update(industry=default_industry)
    if crop_types_updated > 0:
        print(f"✅ Assigned industry to {crop_types_updated} crop types")


def reverse_remove_industry(apps, schema_editor):
    """Reverse: clear industry, then drop industry_id if we added it."""
    CropType = apps.get_model('farms', 'CropType')
    CropType.objects.all().update(industry=None)
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE farms_croptype DROP COLUMN IF EXISTS industry_id
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0016_change_croptype_to_choice_fields'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(safe_add_industry_and_assign, reverse_remove_industry),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='croptype',
                    name='industry',
                    field=models.ForeignKey(
                        blank=True,
                        help_text='Industry this crop type belongs to',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='crop_types',
                        to='users.industry',
                    ),
                ),
            ],
        ),
    ]

