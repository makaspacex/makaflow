import glob
import os
from pathlib import Path

import requests
from ruamel.yaml import YAML

from apps.makaflow import configs
from apps.makaflow.tasks.base import BaseTask
from apps.makaflow.tools.geo import load_geoips, load_geosites
from apps.makaflow.models import Template


def load_env(env_path="env.yaml"):
    yaml = YAML()
    print(f"loading env form {env_path}")
    env_config = yaml.load(open(env_path, 'r'))
    configs.env = env_config
    return env_config

def load_geo():
    geosite_file = configs.env['geosite_file']
    geoip_file = configs.env['geoip_file']
    if not Path(geosite_file).exists():
        resp = requests.get(
            "https://gh-proxy.com/https://github.com/MetaCubeX/meta-rules-dat/releases/download/latest/geosite.dat")
        os.makedirs(Path(geosite_file).parent, exist_ok=True)
        with open(geosite_file, "wb") as f:
            f.write(resp.content)

    if not Path(geoip_file).exists():
        resp = requests.get(
            "https://gh-proxy.com/https://github.com/MetaCubeX/meta-rules-dat/releases/download/latest/geoip.dat")
        os.makedirs(Path(geoip_file).parent, exist_ok=True)
        with open(geoip_file, "wb") as f:
            f.write(resp.content)

    print(f"loading geosites from {geosite_file}")
    configs.geosites = load_geosites(geosite_file)
    print(f"loading geoips from {geoip_file}")
    configs.geoips = load_geoips(geoip_file)


class LoadBigContentThread(BaseTask):
    def __init__(self) -> None:
        super().__init__()

    def run(self):
        try:
            load_geo()
        except Exception as e:
            self.error(e)
        self.info("已停止")


def load_all():
    # 加载env文件
    load_env()
    # 加载geo文件
    load_geo()
