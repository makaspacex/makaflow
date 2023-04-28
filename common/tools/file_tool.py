#! /usr/bin/python
# -*- coding: utf-8 -*-
# @author izhangxm
# @date 2021/4/16
# @fileName file_tool.py
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
import glob
import hashlib
import os


def getFileList(glob_path, exts=None, ignore_case=True, recursive=False):
    glob_func = glob.glob
    if ignore_case:
        glob_func = glob.iglob

    file_list = []
    if exts:
        for ext in exts:
            file_list += list(glob_func(os.path.join(glob_path, f"**/*.{ext}"), recursive=recursive))
    else:
        file_list += list(glob_func(os.path.join(glob_path), recursive=recursive))

    return file_list


def getFileSize(filepath):
    stat_info = os.stat(filepath)
    file_size = stat_info.st_size
    return file_size


def getSuffix(filePath):
    suffix = filePath.split('.')[-1]
    return suffix


def getBigFileMD5(filepath):
    md5obj = hashlib.md5()
    maxbuf = 8192
    f = open(filepath, 'rb')
    while True:
        buf = f.read(maxbuf)
        if not buf:
            break
        md5obj.update(buf)
    f.close()
    hash = md5obj.hexdigest()
    return str(hash).upper()
