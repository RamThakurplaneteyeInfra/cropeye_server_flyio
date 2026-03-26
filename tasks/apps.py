from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    verbose_name = 'Task Management'

    def ready(self):
        import tasks.signals  # noqa: F401 - register post_save for Task -> Notification 