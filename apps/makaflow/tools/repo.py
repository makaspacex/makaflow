import glob
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


class RepoTool():
    def __init__(self, url, path, cwd="./", branch=None) -> None:
        self.url = url
        self.cwd = Path(cwd)
        self.path = Path(path)
        self.branch = branch

    def _exec_cmd(self, cwd, cmd, timeout=None):
        p = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait(timeout=timeout)
        console_out = p.communicate(timeout=timeout)[0].decode('utf8')
        if p.returncode != 0:
            print(console_out)
            raise Exception(f"命令执行发生错误{cmd}")
        return console_out

    def pull(self):
        path = self.path
        if not path.exists():
            raise Exception("仓库文件夹不存在")
        branch = self.get_branch()
        cmd = f"git fetch origin {branch} && git reset --hard origin/{branch}"
        console_out = self._exec_cmd(self.path, cmd)
        return console_out

    def get_branch(self):
        path = self.path
        if not path.exists():
            raise Exception("仓库文件夹不存在")
        cmd = f"git branch"
        console_out = self._exec_cmd(self.path, cmd)
        lines = console_out.split("\n")
        ret = None
        for line in lines:
            if not line.startswith("*"):
                continue
            ret = line.split(" ")[-1]
            break
        if not ret:
            raise Exception("未找到branch")
        if self.branch and ret != self.branch:
            raise Exception("与规定的branch不一致")
        return ret

    def clone(self):
        path = self.path
        if not path.parent.exists():
            os.makedirs(path.parent, exist_ok=True)
        opts = ""
        if self.branch:
            opts += f"--branch={self.branch}"
        cmd = f"git clone --depth=1 {opts} {self.url} {self.path}"
        console_out = self._exec_cmd(self.cwd, cmd, timeout=600)
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
    print(repotool.update())

    print("fff")
