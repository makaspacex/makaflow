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

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_NAME = os.path.split(BASE_DIR)[-1]

NULL_STR = "NULL-121-KOODK"
AUTH_KEY_PREFIX = 'MEDIAAI-FD-'
context = {
    'NULL_STR': NULL_STR,
    'AUTH_KEY_PREFIX': AUTH_KEY_PREFIX
}
TMP_DIR = os.path.join(BASE_DIR, 'runtime', 'tmp')

APPS_DIR = BASE_DIR/"apps"
APP_NAMES = []
for _d in APPS_DIR.iterdir():
    if not _d.is_dir():
        continue
    if _d.name.startswith('.') or _d.name.startswith('_'):
        continue
    APP_NAMES.append(f"apps.{_d.name}")

