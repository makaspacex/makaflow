#! /usr/bin/python
# -*- coding: utf-8 -*-
# @author izhangxm
# @date 2021/4/15
# @fileName config.py
# Copyright 2017 izhangxm@gmail.com. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import os
from pathlib import Path

import os
import glob

import ruamel.yaml
yaml = ruamel.yaml.YAML()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_NAME = os.path.split(BASE_DIR)[-1]

# github仓库更新线程
_repo_thrds={}

# 订阅更新线程
_sub_thrd = {}

# env file
env={}

# 加载订阅模板文件
sub_tps = {}

# geoips
geoips = {}
geosites= {}
