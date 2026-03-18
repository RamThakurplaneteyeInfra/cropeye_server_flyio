# Generated manually for optional Aadhaar field (additive only).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='aadhaar_number',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='Optional. 12-digit Aadhaar (stored without spaces).',
                max_length=12,
                null=True,
                unique=True,
            ),
        ),
    ]
