# Generated manually - add sugarcane and grapes fields to Farm model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0018_add_crop_variety_to_farm'),
    ]

    operations = [
        migrations.AddField(
            model_name='farm',
            name='sugarcane_plantation_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', '---------'),
                    ('adsali', 'Adsali'),
                    ('suru', 'Suru'),
                    ('ratoon', 'Ratoon'),
                    ('pre-seasonal', 'Pre-Seasonal'),
                    ('post-seasonal', 'Post-Seasonal'),
                    ('pre_seasonal', 'Pre-Seasonal'),
                    ('other', 'Other'),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='sugarcane_planting_method',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', '---------'),
                    ('3_bud', '3 Bud Method'),
                    ('2_bud', '2 Bud Method'),
                    ('1_bud', '1 Bud Method'),
                    ('1_bud_stip_Method', '1 Bud (stip Method)'),
                    ('other', 'Other'),
                ],
                max_length=30,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='grapes_plantation_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', '---------'),
                    ('wine', 'Wine Grapes'),
                    ('table', 'Table Grapes'),
                    ('late', 'Late'),
                    ('early', 'Early'),
                    ('pre_season', 'Pre-Season'),
                    ('seasonal', 'Seasonal'),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='variety_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('pre_season', 'Pre-season'),
                    ('seasonal', 'Seasonal'),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='variety_subtype',
            field=models.CharField(
                blank=True,
                choices=[
                    ('wine_grapes', 'Wine Grapes'),
                    ('table_grapes', 'Table Grapes'),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='variety_timing',
            field=models.CharField(
                blank=True,
                choices=[
                    ('early', 'Early'),
                    ('late', 'Late'),
                ],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='plant_age',
            field=models.CharField(
                blank=True,
                choices=[
                    ('0_2', '0-2 years'),
                    ('2_3', '2-3 years'),
                    ('above_3', 'Above 3 years'),
                ],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='foundation_pruning_date',
            field=models.DateField(
                blank=True,
                help_text='Foundation pruning date (Grapes only)',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='fruit_pruning_date',
            field=models.DateField(
                blank=True,
                help_text='Fruit pruning date (Grapes only)',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='last_harvesting_date',
            field=models.DateField(
                blank=True,
                help_text='Last harvesting date (Grapes only)',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='resting_period_days',
            field=models.IntegerField(
                blank=True,
                help_text='Resting period in days (Grapes only)',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='row_spacing',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Row spacing in meters (Grapes drip irrigation)',
                max_digits=8,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='plant_spacing',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Plant spacing in meters (Grapes drip irrigation)',
                max_digits=8,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='flow_rate_liter_per_hour',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Flow rate in liters/hour (Grapes drip irrigation)',
                max_digits=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='farm',
            name='emitters_per_plant',
            field=models.IntegerField(
                blank=True,
                help_text='Number of emitters per plant (Grapes drip irrigation)',
                null=True,
            ),
        ),
    ]
