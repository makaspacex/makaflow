import threading
import time
from apps.makaflow import configs
import os
import subprocess
import sys

class UpdateBm7RepoThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print(f"Task: {self.__class__.__name__} stated")
        env = configs.env
        rule_repo_dir = env['rule_repo_dir']
        cmd_clone = "git clone --depth=1 https://github.com/blackmatrix7/ios_rule_script.git"
        cmd_pull = "git pull"
        
        repo_dir = f"{rule_repo_dir}/ios_rule_script"
        
        while True:
            try:
                print(f"Task: {self.__class__.__name__} start running...")
                cmd = cmd_pull
                cwd = repo_dir
                
                if not os.path.exists(repo_dir):
                    cmd = cmd_clone
                    cwd = rule_repo_dir
                
                # p = subprocess.Popen(cmd, shell=True, cwd=cwd,  stdout=sys.stdout, stderr=sys.stdout)
                p = subprocess.Popen(cmd, shell=True, cwd=cwd,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p.wait()
                
                print(p.communicate()[0].decode('utf8'))
                
            except Exception as e:
                print(e)

            # time.sleep(5)
            time.sleep(60 * 60 *12)
