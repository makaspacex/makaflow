import glob
import os
import time
from pathlib import Path

import requests
from ruamel.yaml import YAML

from apps.makaflow import configs
from apps.makaflow.tasks.base import BaseTask
from apps.makaflow.tools.geo import load_geoips, load_geosites
from apps.makaflow.models import Template
from common.models import Config

def load_env(env_path="env.yaml"):
    yaml = YAML()
    print(f"loading env form {env_path}")
    env_config = yaml.load(open(env_path, 'r'))
    configs.env = env_config
    return env_config

def load_geo():
    geosite_file = Config.get("geosite_file","runtime/resource/meta-rules-dat/geosite.dat")
    geoip_file = Config.get("geoip_file","runtime/resource/meta-rules-dat/geoip.dat")
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
            time.sleep(1)
        self.info("已停止")

def load_all():
    # 加载env文件
    load_env()
    # 加载geo文件
    load_geo()
