import threading
from  apps.makaflow.tools.subscrib_common import update_subscribe_cache
import time

class UpdateSubThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print(f"Task: {self.__class__.__name__} stated")
        while True:
            try:
                update_subscribe_cache()
            except Exception:
                pass

            time.sleep(10)
