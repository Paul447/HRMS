from django.apps import AppConfig


class PtobalanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ptobalance"

    def ready(self):
        from HRMS.scheduler import start_scheduler

        start_scheduler()
