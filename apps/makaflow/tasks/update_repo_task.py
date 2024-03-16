import glob
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

from apps.makaflow import configs
from apps.makaflow.models import Repo
from apps.makaflow.tasks.base import BaseTask
from apps.makaflow.tools.repo import RepoTool
from common.models import Config


class UpdateRepoThread(BaseTask):

    def __init__(self, repo: Repo, init_update=False) -> None:
        super().__init__(name=repo.name)
        self.repo = repo
        self.init_update = init_update

    def run(self):
        self.info("已启动")
        while not self._kill.is_set():
            try:
                parent_path = Path(Config.get("resource_dir", "runtime/resource"))
                repo_tool = RepoTool(url=self.repo.url, path=parent_path / self.repo.path, branch=self.repo.branch)
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
                now = datetime.now(last_update.tzinfo)
                diff_seconds = (now - last_update).total_seconds()
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
            # 更新当前的对象
            self.repo = Repo.objects.get(pk=self.repo.pk)
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
    # from common.tools import init_django_env
    # init_django_env("Makaflow.settings")

    # repos = Repo.objects.all()
    # repo = repos[1]
    # thrd = UpdateRepoThread(repo=repo)
    # thrd.start()
    # thrd.join()
    url = "https://gh-proxy.com/https://github.com/sub-store-org/Sub-Store.git "
    path = "runtime/resource/Sub-Store"
    repotool = RepoTool(url=url, path=path, branch="release")
    brach = repotool.get_branch()
    print(brach)
    print("fff")
