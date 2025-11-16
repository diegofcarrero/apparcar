from django.apps import AppConfig

class ApparcarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apparcar'

    def ready(self):
        # importa signals para registrarlas
        import apparcar.signals  # noqa
