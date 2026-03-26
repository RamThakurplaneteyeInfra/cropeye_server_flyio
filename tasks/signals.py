"""
Signals for tasks app.
Creates a Notification only when a Grapes industry field officer assigns a task to a farmer.
Does not affect other industries or roles.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Task, Notification


@receiver(post_save, sender=Task)
def create_notification_on_task_assignment(sender, instance, created, **kwargs):
    """
    When a new task is created: if it is a Grapes industry task, created by a
    field officer, and assigned to a farmer, create one Notification for that farmer.
    Other industries (e.g. sugarcane) and other flows are unaffected.
    """
    if not created:
        return
    if not instance.assigned_to_id:
        return
    # Only for Grapes industry
    if not instance.industry or getattr(instance.industry, 'crop_type', None) != 'grapes':
        return
    # Creator must be field officer, assignee must be farmer
    created_by = instance.created_by
    assigned_to = instance.assigned_to
    if not (created_by and created_by.has_role('fieldofficer')):
        return
    if not (assigned_to and assigned_to.has_role('farmer')):
        return
    Notification.objects.create(
        user=assigned_to,
        message=f"New task assigned: {instance.title}",
        related_task=instance,
    )
