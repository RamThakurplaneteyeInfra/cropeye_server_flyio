from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Equipment, MaintenanceRecord, EquipmentUsage
from .serializers import (
    EquipmentSerializer,
    EquipmentCreateSerializer,
    EquipmentUpdateSerializer,
    MaintenanceRecordSerializer,
    MaintenanceRecordCreateSerializer,
    EquipmentUsageSerializer,
    EquipmentUsageCreateSerializer
)
from .permissions import CanManageEquipment, CanViewEquipment

class EquipmentViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return EquipmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EquipmentUpdateSerializer
        return EquipmentSerializer

    def get_permissions(self):
        action = getattr(self, 'action', 'list')
        if action in ['create', 'destroy']:
            return [CanManageEquipment()]
        elif action in ['update', 'partial_update']:
            return [CanManageEquipment()]
        return [CanViewEquipment()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.has_role('owner') or user.has_role('manager'):
            return Equipment.objects.all()
        elif user.has_role('fieldofficer'):
            return Equipment.objects.filter(
                Q(assigned_to=user) | Q(status='available')
            )
        return Equipment.objects.filter(status='available')

    @action(detail=True, methods=['post'])
    def add_maintenance_record(self, request, pk=None):
        equipment = self.get_object()
        serializer = MaintenanceRecordCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(equipment=equipment, performed_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def start_usage(self, request, pk=None):
        equipment = self.get_object()
        if equipment.status != 'available':
            return Response(
                {'error': 'Equipment is not available for use.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = EquipmentUsageCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(equipment=equipment, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def end_usage(self, request, pk=None):
        equipment = self.get_object()
        if equipment.status != 'in_use' or equipment.assigned_to != request.user:
            return Response(
                {'error': 'Equipment is not in use by this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        usage = EquipmentUsage.objects.filter(
            equipment=equipment,
            user=request.user,
            end_date__isnull=True
        ).first()
        if not usage:
            return Response(
                {'error': 'No active usage record found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        usage.end_date = request.data.get('end_date')
        usage.save()
        serializer = EquipmentUsageSerializer(usage)
        return Response(serializer.data)

class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageEquipment]

    def get_queryset(self):
        return MaintenanceRecord.objects.filter(equipment_id=self.kwargs['equipment_pk'])

    def perform_create(self, serializer):
        equipment = get_object_or_404(Equipment, pk=self.kwargs['equipment_pk'])
        serializer.save(equipment=equipment, performed_by=self.request.user)

class EquipmentUsageViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentUsageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EquipmentUsage.objects.filter(equipment_id=self.kwargs['equipment_pk'])

    def perform_create(self, serializer):
        equipment = get_object_or_404(Equipment, pk=self.kwargs['equipment_pk'])
        serializer.save(equipment=equipment, user=self.request.user) 