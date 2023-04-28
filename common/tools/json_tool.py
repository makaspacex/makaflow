#! /usr/bin/python
# -*- coding: utf-8 -*-
# @author izhangxm
# @date 2021/5/21
# @fileName json_tool.py
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
import re


def pyjson2jsstr(pyjson_str_or_obj):
    if isinstance(pyjson_str_or_obj, dict):
        pyjson_str_or_obj = str(pyjson_str_or_obj)
    res = re.sub(r'"(.*?)":', r'\1:', pyjson_str_or_obj)
    # print(res)
    res = re.sub(r"'(\w+?)':", r'\1:', res)
    res = re.sub(r"False", r'false', res)
    res = re.sub(r"True", r'true', res)
    return res


def jsstr2pyjson(jsstr):
    res = re.sub(r'(\w+?):', r'"\1":', jsstr)
    res = re.sub(r"'", r'"', res)
    res = re.sub(r"(\S),([\s]*?)}", r'\1\2}', res)
    res = re.sub(r"(\.[\d]+)", r'0\1', res)
    res = re.sub(r"False", r'false', res)
    res = re.sub(r"True", r'true', res)
    res = json.loads(res)
    return res


if __name__ == '__main__':
    from common.config import BASE_DIR
    import json

    fp = open(os.path.join(BASE_DIR, "testingsystem/data/project_details_tp.js"), 'r', encoding='utf-8')
    js_str = fp.read()
    pyjson = jsstr2pyjson(js_str)

    print(json.dumps(pyjson))

    print(pyjson2jsstr(pyjson))

    fp.close()
