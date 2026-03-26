from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    TaskViewSet,
    TaskCommentViewSet,
    TaskAttachmentViewSet,
    NotificationListView,
    NotificationUnreadListView,
    NotificationUnreadCountView,
    NotificationMarkReadView,
)

router = routers.SimpleRouter()
router.register(r'', TaskViewSet, basename='task')

nested_router = routers.NestedSimpleRouter(router, r'', lookup='task')
nested_router.register(r'comments', TaskCommentViewSet, basename='task-comment')
nested_router.register(r'attachments', TaskAttachmentViewSet, basename='task-attachment')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(nested_router.urls)),
    # Notification (alert) API - Grapes industry farmer / field officer only
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/unread/', NotificationUnreadListView.as_view(), name='notification-unread'),
    path('notifications/unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    path('notifications/<int:pk>/mark-read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
] 