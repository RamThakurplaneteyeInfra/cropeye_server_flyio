from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Equipment, MaintenanceRecord, EquipmentUsage

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')

class MaintenanceRecordSerializer(serializers.ModelSerializer):
    performed_by = UserSerializer(read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = ('id', 'performed_by', 'maintenance_date', 'description',
                 'cost', 'next_maintenance_date', 'created_at')
        read_only_fields = ('created_at',)

class EquipmentUsageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = EquipmentUsage
        fields = ('id', 'user', 'start_date', 'end_date', 'purpose', 'created_at')
        read_only_fields = ('created_at',)

class EquipmentSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    maintenance_records = MaintenanceRecordSerializer(many=True, read_only=True)
    usage_records = EquipmentUsageSerializer(many=True, read_only=True)

    class Meta:
        model = Equipment
        fields = ('id', 'name', 'description', 'status', 'purchase_date',
                 'purchase_price', 'location', 'assigned_to',
                 'last_maintenance_date', 'next_maintenance_date',
                 'created_at', 'updated_at', 'maintenance_records', 'usage_records')
        read_only_fields = ('created_at', 'updated_at', 'last_maintenance_date',
                          'next_maintenance_date')

class EquipmentCreateSerializer(serializers.ModelSerializer):
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True,
        required=False
    )

    class Meta:
        model = Equipment
        fields = ('name', 'description', 'status', 'purchase_date',
                 'purchase_price', 'location', 'assigned_to_id')

class EquipmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ('name', 'description', 'status', 'location', 'assigned_to')

class MaintenanceRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = ('maintenance_date', 'description', 'cost', 'next_maintenance_date')

class EquipmentUsageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentUsage
        fields = ('start_date', 'end_date', 'purpose') 