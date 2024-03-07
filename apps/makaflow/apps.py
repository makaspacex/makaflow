from django.apps import AppConfig
import sys

class MakaflowConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.makaflow"
    verbose_name = "玛卡订阅"
    def ready(self) -> None:
        super().ready()
        try:
            # 判断是否是runserver
            argv = sys.argv or sys.argv[:]
            sub_cmd = None
            if isinstance(argv, list) and len(argv)>=2:
                sub_cmd = argv[1]
            if sub_cmd == 'runserver':
                from apps.makaflow.tasks import start_all_tasks
                from apps.makaflow.tasks.load_file_init import load_env
                load_env()
                start_all_tasks()
        except Exception as e:
            print(e)