from django.db import models
from django.conf import settings

class Equipment(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    )

    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

class MaintenanceRecord(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_records')
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    maintenance_date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    next_maintenance_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-maintenance_date']

    def __str__(self):
        return f"Maintenance for {self.equipment.name} on {self.maintenance_date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update equipment's last and next maintenance dates
        self.equipment.last_maintenance_date = self.maintenance_date
        self.equipment.next_maintenance_date = self.next_maintenance_date
        self.equipment.save()

class EquipmentUsage(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='usage_records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    purpose = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.equipment.name} used by {self.user.username} from {self.start_date}"

    def save(self, *args, **kwargs):
        if not self.end_date:
            # Update equipment status to 'in_use' when usage starts
            self.equipment.status = 'in_use'
            self.equipment.assigned_to = self.user
            self.equipment.save()
        else:
            # Update equipment status to 'available' when usage ends
            self.equipment.status = 'available'
            self.equipment.assigned_to = None
            self.equipment.save()
        super().save(*args, **kwargs) 