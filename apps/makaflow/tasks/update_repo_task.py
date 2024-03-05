import time
from apps.makaflow import configs
import os
import subprocess
import glob
from pathlib import Path
import json
from apps.makaflow.tasks.base import BaseTask
from apps.makaflow.models import Repo
from pathlib import Path

class UpdateRepoThread(BaseTask):
    
    def __init__(self, repo:Repo) -> None:
        super().__init__(name=repo.name)
        self.repo = repo
    
    def run(self):

        while not self._kill.is_set():
            try:
                path = Path(self.repo.path)
                cmd = "git pull --allow-unrelated-histories"
                cwd = self.repo.path
                
                if not path.exists():
                    # 克隆到目标文件夹
                    cmd = f"git clone --depth=1 {self.repo.url} {self.repo.path}"
                    cwd = "./"
                
                p = subprocess.Popen(cmd, shell=True, cwd=cwd,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p.wait()
                self.info(p.communicate()[0].decode('utf8'))
                
            except Exception as e:
                self.error(e)
            self.sleep(self.repo.interval)
        
        self.info("stoped")
        
class UpdateQureRepoThread(BaseTask):
   
    def update_json(self, repo_dir, out_path):
        repo_dir = Path(repo_dir)
        icon_dir = f"{repo_dir}/IconSet"
        png_paths = list(glob.glob(f"{icon_dir}/**/*.png", recursive=True))
        res = {"name": "Maka Gallery", "description": "Makaflow收集互联网公开图标文件，版权属于原作者和商标持有人。"}
        icons = []
        env = configs.env
        icon_base_url = env['icon_base_url']
        for path in png_paths:
            path = path.replace(f"{repo_dir.parent}/", "")
            path = Path(path)
            
            new_name = "_".join(path.parts)
            d_path = "/".join(path.parts)
            downw_url = f"{icon_base_url}/{d_path}"
            icons.append({"name":new_name, "url":downw_url})

        res['icons'] = icons
        os.makedirs(Path(out_path).parent, exist_ok=True)
        json.dump(res, open(f"{out_path}", 'w+'))
        return res
    
    def run(self):
        task_name = f"{self.__class__.__name__}"
        
        env = configs.env
        icon_repo_dir = env['icon_repo_dir']
        cmd_clone = "git clone --depth=1 https://github.com/Koolson/Qure.git"
        cmd_pull = "git pull --allow-unrelated-histories"
        
        repo_dir = f"{icon_repo_dir}/Qure"
        icon_json_path= env['icon_json']
        
        
        while True:
            try:
                self.info(f"INFO:[{task_name}] start running...")
                cmd = cmd_pull
                cwd = repo_dir
                
                if not os.path.exists(repo_dir):
                    cmd = cmd_clone
                    cwd = icon_repo_dir
                    os.makedirs(Path(repo_dir).parent, exist_ok=True)
                
                # p = subprocess.Popen(cmd, shell=True, cwd=cwd,  stdout=sys.stdout, stderr=sys.stdout)
                p = subprocess.Popen(cmd, shell=True, cwd=cwd,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p.wait()
                
                self.info(f"{p.communicate()[0].decode('utf8')}")
                
                self.update_json(repo_dir=repo_dir, out_path=icon_json_path)
                
            except Exception as e:
                self.error(f"{e}")

            # time.sleep(5)
            time.sleep(60 * 60 *24)
