from django.contrib import admin
from .models import Equipment, MaintenanceRecord, EquipmentUsage

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'location', 'assigned_to', 'last_maintenance_date', 'next_maintenance_date')
    list_filter = ('status', 'assigned_to', 'location')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    raw_id_fields = ('assigned_to',)

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'performed_by', 'maintenance_date', 'cost', 'next_maintenance_date')
    list_filter = ('performed_by', 'maintenance_date')
    search_fields = ('description', 'equipment__name')
    ordering = ('-maintenance_date',)
    raw_id_fields = ('equipment', 'performed_by')

@admin.register(EquipmentUsage)
class EquipmentUsageAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'user', 'start_date', 'end_date')
    list_filter = ('user', 'start_date', 'end_date')
    search_fields = ('purpose', 'equipment__name', 'user__username')
    ordering = ('-start_date',)
    raw_id_fields = ('equipment', 'user') 