from django.apps import AppConfig


class MakaflowConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.makaflow"
    verbose_name = "玛卡订阅"
    def ready(self) -> None:
        super().ready()
        try:
            from apps.makaflow.tasks import start_all_tasks
            from apps.makaflow.tasks import load_all
            # load_all()
            start_all_tasks()
            
        except Exception as e:
            print(e)