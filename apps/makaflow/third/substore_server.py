from collections.abc import Callable, Iterable, Mapping
import threading
import time
from typing import Any
from apps.makaflow import configs
import os
import subprocess
import sys
import glob
from pathlib import Path
import json
from apps.makaflow.tasks.base import BaseTask
import subprocess
from subprocess import Popen
from subprocess import PIPE
from pathlib import Path

class ProxyConverServer(BaseTask):

    def run(self):
        from apps.makaflow.configs import env
        node_exe = env['node_exe']
        cmd = [f"{node_exe}", "../apps/makaflow/third/sub-store.bundle.js"]
        cwd = "./runtime"
        my_env = os.environ.copy()
        my_env["SUB_STORE_BACKEND_API_PORT"] = str(env['SUB_STORE_BACKEND_API_PORT'])
        self.process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=my_env)
        
        while True:
            try:
                line = self.process.stdout.readline().decode("utf8").strip()
                ret_code = self.process.poll()
                if line == '' and ret_code is not None:
                    break
                self.info(line)
            except Exception as e:
                self.error(e)
            time.sleep(0.1)
        raise Exception("服务异常退出....")
    
if __name__ == "__main__":
    a = ProxyConverServer()
    a.start()
    print("Exiting Main Thread")
    
    
    
    