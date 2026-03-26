from django import forms
from django.core.exceptions import ValidationError
from .models import PlantationRecord

class PlantationRecordForm(forms.ModelForm):
    class Meta:
        model = PlantationRecord
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        farm = cleaned_data.get("farm")

        if not farm or not farm.plant_age:
            raise ValidationError("Farm must have a valid plant age set.")

        farm_age = farm.plant_age  # '0_2' or '2_13'

        # Determine plantation type based on farm_age
        if farm_age == "0_2":
            # New Plantation
            cleaned_data["source_type"] = "new"
            required_fields = [
                "plantation_date",
                "rootstock",
                "grafting_date",
                "grafted_variety",
                "soil_type",
                "foundation_pruning_date",
                "fruit_pruning_date",
            ]
        elif farm_age == "2_13":
            # Registration
            cleaned_data["source_type"] = "registration"
            required_fields = [
                "plantation_date",
                "grafted_variety",
                "soil_type",
                "foundation_pruning_date",
                "fruit_pruning_date",
                "irrigation_type",
                "last_harvesting_date",
                "intercropping",
            ]
        else:
            raise ValidationError("Plant age of farm is invalid.")

        # Check for missing required fields
        missing_fields = [f for f in required_fields if not cleaned_data.get(f)]
        for field_name in missing_fields:
            self.add_error(
                field_name,
                "This field is required for this type of plantation."
            )
