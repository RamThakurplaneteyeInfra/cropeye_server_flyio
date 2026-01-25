from django.urls import path, include
from rest_framework_nested import routers
from .views import EquipmentViewSet, MaintenanceRecordViewSet, EquipmentUsageViewSet

router = routers.SimpleRouter()
router.register(r'equipment', EquipmentViewSet, basename='equipment')

equipment_router = routers.NestedSimpleRouter(router, r'equipment', lookup='equipment')
equipment_router.register(r'maintenance-records', MaintenanceRecordViewSet, basename='maintenance-record')
equipment_router.register(r'usage-records', EquipmentUsageViewSet, basename='usage-record')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(equipment_router.urls)),
] 