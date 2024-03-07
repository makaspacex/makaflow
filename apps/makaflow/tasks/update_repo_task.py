import glob
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from apps.makaflow import configs
from apps.makaflow.models import Repo
from apps.makaflow.tasks.base import BaseTask


class RepoTool():
    def __init__(self, url, path, cwd="./") -> None:
        self.url = url
        self.cwd = Path(cwd)
        self.path = Path(path)

    def _exec_cmd(self, cwd, cmd):
        p = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        console_out = p.communicate()[0].decode('utf8')
        if p.returncode != 0:
            print(console_out)
            raise Exception(f"命令执行发生错误{cmd}")
        return console_out

    def pull(self):
        path = self.path
        if not path.exists():
            raise Exception("仓库文件夹不存在")
        cmd = f"git pull --allow-unrelated-histories"
        console_out = self._exec_cmd(self.path, cmd)
        return console_out

    def clone(self):
        path = self.path
        if not path.parent.exists():
            os.makedirs(path.parent, exist_ok=True)
        cmd = f"git clone {self.url} {self.path}"
        console_out = self._exec_cmd(self.cwd, cmd)
        return console_out

    def get_version(self):
        if not self.path.exists():
            return None
        cmd = "git log | grep commit | head -n 2"
        console_out = self._exec_cmd(self.cwd / self.path, cmd)
        version = console_out.split("\n")[0].split(" ")[-1][:8]
        return version

    def update(self):
        path = self.path
        if not path.exists():
            self.clone()
        else:
            self.pull()


class UpdateRepoThread(BaseTask):

    def __init__(self, repo: Repo, init_update=False) -> None:
        super().__init__(name=repo.name)
        self.repo = repo
        self.init_update = init_update

    def run(self):
        self.info("已启动")
        repo_tool = RepoTool(url=self.repo.url, path=self.repo.path, cwd="./")
        while not self._kill.is_set():
            try:
                if not self.repo.autoupdate:
                    self.info("读取到设置为禁止自动更新，即将退出")
                    break
                self.info(f"repourl:{self.repo.url}")
                path = Path(self.repo.path)

                # 计算等待时间，防止频繁更新
                waittime = self.repo.interval
                force_update = False

                version = repo_tool.get_version()
                if not path.exists() or self.repo.version != version:
                    force_update = True

                last_update = self.repo.updated_at
                now = datetime.now(timezone.utc)
                diff_seconds = (now - last_update).seconds
                if not force_update and diff_seconds < self.repo.interval:
                    waittime = self.repo.interval - diff_seconds
                    raise Exception(f"间隔时间过短，等待{waittime}后更新")

                repo_tool.update()
                # 获取提交的版本号
                version = repo_tool.get_version()
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
            icons.append({"name": new_name, "url": downw_url})

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
        icon_json_path = env['icon_json']

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
                p = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p.wait()

                self.info(f"{p.communicate()[0].decode('utf8')}")

                self.update_json(repo_dir=repo_dir, out_path=icon_json_path)

            except Exception as e:
                self.error(f"{e}")

            # time.sleep(5)
            time.sleep(60 * 60 * 24)


if __name__ == "__main__":
    repos = Repo.objects.all()
    repo = repos[1]
    thrd = UpdateRepoThread(repo=repo)
    thrd.start()
    thrd.join()

    print("fff")
