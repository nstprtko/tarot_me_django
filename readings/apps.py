from django.apps import AppConfig


class ReadingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'readings'

    def ready(self):
        # for signals.py - import signals so they are registered
        import readings.signals
