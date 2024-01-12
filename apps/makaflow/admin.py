#! /usr/bin/python
# -*- coding: utf-8 -*-
# @author izhangxm
# @date 2021/12/6
# @fileName admin.py
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

from django.contrib import admin
from django.apps import apps as dj_apps

from .models import *

from common.admin import BaseAdmin


@admin.register(Subscribe)
class SubscribeAdmin(BaseAdmin):
    list_display = ['id', 'name', 'sub_enable', 'prefix', 'sub_url' ]
    fields = ['name', 'sub_enable', 'prefix', 'sub_url', 'node_excludes', 'repl_names', 'content','server_mirr']
    
    
@admin.register(Rule)
class RuleAdmin(BaseAdmin):
    list_display = ['id', 'name', 'rule']
    fields = ['name', 'rule', ]

