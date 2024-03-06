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
from datetime import datetime,timezone



class UpdateRepoThread(BaseTask):
    
    def __init__(self, repo:Repo) -> None:
        super().__init__(name=repo.name)
        self.repo = repo
    
    def run(self):
        self.info("已启动")
        while not self._kill.is_set():
            try:
                if not self.repo.autoupdate:
                    self.info("读取到设置为禁止自动更新，即将退出")
                    break
                
                self.info(f"repourl:{self.repo.url}")
                
                # 计算等待时间，防止频繁更新
                waittime = self.repo.interval
                last_update = self.repo.updated_at
                now = datetime.now(timezone.utc)
                diff_seconds = (now - last_update).seconds
                if diff_seconds<self.repo.interval:
                    waittime = self.repo.interval - diff_seconds
                    raise Exception(f"间隔时间过短，等待{waittime}后更新")
                
                path = Path(self.repo.path)
                cmd = "git pull --allow-unrelated-histories"
                cwd = self.repo.path
                
                if not path.exists():
                    # 克隆到目标文件夹
                    cmd = f"git clone --depth=1 {self.repo.url} {self.repo.path}"
                    cwd = "./"
                
                p = subprocess.Popen(cmd, shell=True, cwd=cwd,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p.wait()
                console_out = p.communicate()[0].decode('utf8')
                
                self.info(f"控制台输出:\n{console_out}")
                
                # 获取提交的版本号
                p = subprocess.Popen("git log | grep commit", shell=True, cwd= self.repo.path,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p.wait()
                console_out = p.communicate()[0].decode('utf8')
                version = console_out.split("\n")[0].split(" ")[-1][:8]
                if self.repo.version != version:
                    self.repo.version = version
                    
                    self.info(f"已更新到最新版 当前最新版本是{version}")
                else:
                    self.info(f"无更新 当前最新版本是{version}")
                self.repo.save()
            except Exception as e:
                self.error(e)
            
            self.sleep(waittime)
        
        self.info("已停止")

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
