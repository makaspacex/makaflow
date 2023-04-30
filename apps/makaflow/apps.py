from django.apps import AppConfig
from apps.makaflow.tools.subscrib_common import start_tasks
class MakaflowConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.makaflow"
    verbose_name = "Makaflow"
    def ready(self) -> None:
        super().ready()
        from apps.makaflow import urls
        try:
            urls.init()
            start_tasks()
            
        except Exception as e:
            print(e)