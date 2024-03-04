from django.apps import AppConfig
from apps.makaflow.tasks import start_tasks
from apps.makaflow.tasks import load_all
from apps.makaflow.tasks import *
from apps.makaflow.tasks import load_env,load_users,load_third_sub_profile,load_sub_tps

class MakaflowConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.makaflow"
    verbose_name = "玛卡订阅"
    def ready(self) -> None:
        super().ready()
        try:
            pass
            load_all()
            # start_tasks()
        except Exception as e:
            print(e)