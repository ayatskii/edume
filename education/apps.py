from django.apps import AppConfig


class EducationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'education'

    def ready(self):
        # Import signals to ensure they are registered
        import education.signals
