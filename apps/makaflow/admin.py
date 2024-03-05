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
from apps.makaflow import configs
from apps.makaflow.tasks import UpdateRepoThread
import threading
from django.contrib import messages




@admin.register(Subscribe)
class SubscribeAdmin(BaseAdmin):
    list_display = ['id', 'name','sub_groups', 'sub_enable', 'prefix', 'sub_url' ]
    fields = ['name', 'sub_enable', 'prefix', 'sub_url','subscription_userinfo', 'sub_groups', 'repl_names','server_mirr', 'content']

@admin.register(Repo)
class RepoAdmin(BaseAdmin):
    
    def start_update(self, request, queryset):
        try:
            for repo in queryset:
                if repo.id in configs._threadings:
                    _th:UpdateRepoThread = configs._threadings[repo.id]
                    if _th.is_alive():
                        continue
                    else:
                        del _th
                _th = UpdateRepoThread(repo)
                _th.start()
                configs._threadings[repo.id] = _th
            self.message_user(request,"操作成功", messages.SUCCESS)
        except Exception as e:
            self.message_user(request,f"失败:{e}", messages.ERROR)
        
    def stop_update(self, request, queryset):
        try:
            for repo in queryset:
                if repo.id not in configs._threadings:
                    continue
                _th:UpdateRepoThread = configs._threadings[repo.id]
                _th.kill()
                del configs._threadings[repo.id]
                
            self.message_user(request,"操作成功", messages.SUCCESS)
        except Exception as e:
            self.message_user(request,f"失败:{e}", messages.ERROR)

    start_update.short_description = "启动更新线程"
    stop_update.short_description = "停止更新线程"
    
    list_display = ['id', 'name','url', 'path', 'interval', 'version','up_thred_status']
    fields = ['name','url', 'path', 'interval', 'version' ]
    
    actions = [start_update, stop_update]
    
