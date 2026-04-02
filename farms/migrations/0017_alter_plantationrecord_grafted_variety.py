# Generated manually to match PlantationRecord.GRAPE_VARIETY_CHOICES expansion

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0016_add_intercropping_crop_name_and_rootstock_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plantationrecord',
            name='grafted_variety',
            field=models.CharField(
                choices=[
                    ('thompson', 'Thompson'),
                    ('tas_a_ganesh', 'Tas-A-Ganesh'),
                    ('sonaka', 'Sonaka'),
                    ('manik_chaman', 'Manik Chaman'),
                    ('flame_seedless', 'Flame Seedless'),
                    ('crimson_seedless', 'Crimson Seedless'),
                    ('red_globe', 'Red Globe'),
                    ('sudhakar_seedless', 'Sudhakar Seedless'),
                    ('allison', 'Allison'),
                    ('timco', 'Timco'),
                    ('ard_35', 'ARD-35'),
                    ('ard_36', 'ARD-36'),
                    ('thompson_seedless', 'Thompson seedless'),
                    ('super_sonaka', 'super sonaka'),
                    ('crimson', 'Crimson'),
                    ('ssn', 'SSN'),
                    ('sharad_seedless', 'sharad seedless'),
                    ('mama_jambo', 'mama jambo'),
                    ('rk', 'RK'),
                    ('arra_35', 'Arra-35'),
                    ('arra_36', 'Arra-36'),
                    ('grape_1530', '1530'),
                    ('grape_1557', '1557'),
                    ('clone', 'clone'),
                    ('timson', 'Timson'),
                    ('raigad_purple', 'Raigad purple'),
                    ('anushka', 'Anushka'),
                    ('nanasaheb_purple', 'nanasaheb purple'),
                ],
                max_length=30,
            ),
        ),
    ]
