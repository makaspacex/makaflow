import threading
from  apps.makaflow.tools.subscrib_common import update_subscribe_cache
import time
from .base import BaseTask
class UpdateSubThread(BaseTask):
    def run(self):
        while True:
            try:
                update_subscribe_cache()
            except Exception:
                pass
            time.sleep(10)
