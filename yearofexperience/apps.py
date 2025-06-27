from django.apps import AppConfig


class YearofexperienceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "yearofexperience"

    def ready(self):
        import yearofexperience.signals
