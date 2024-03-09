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
from django.contrib import messages

from apps.makaflow import configs
from apps.makaflow.tasks import UpdateRepoThread
from apps.makaflow.tasks import UpdateSubscribeThread
from common.admin import BaseAdmin
from .models import *


@admin.register(Subscribe)
class SubscribeAdmin(BaseAdmin):
    list_display = ['id', 'name', 'order', 'sub_groups', 'sub_enable', 'use_proxy', 'prefix', 'sub_url',
                    'up_thred_status', 'autoupdate', "interval"]
    fields = ['name', 'autoupdate', "interval", 'sub_enable', 'use_proxy', 'order', 'prefix', 'sub_url',
              'subscription_userinfo', 'sub_groups', 'repl_names', 'node_includes', "node_excludes", 'server_mirr',
              'content']
    ordering = ('order',)

    def start_update(self, request, queryset):
        try:
            skips, success = [], []
            for sub in queryset:
                if sub.id in configs._sub_thrd:
                    _th: UpdateSubscribeThread = configs._sub_thrd[sub.id]
                    if _th.is_alive():
                        skips.append(sub.name)
                        continue
                    else:
                        del _th
                _th = UpdateSubscribeThread(sub)
                _th.start()
                configs._sub_thrd[sub.id] = _th
                success.append(sub.name)
            s1 = ",".join(skips[:3])
            s2 = ",".join(success[:3])
            messege = f"成功启动：{s2}等，已跳过:{s1}等"
            self.message_user(request, f"操作成功{messege}", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"失败:{e}", messages.ERROR)

    def stop_update(self, request, queryset):
        try:
            for repo in queryset:
                if repo.id not in configs._sub_thrd:
                    continue
                _th: UpdateSubscribeThread = configs._sub_thrd[repo.id]
                _th.kill()
                del configs._sub_thrd[repo.id]

            self.message_user(request, "操作成功", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"失败:{e}", messages.ERROR)

    start_update.short_description = "启动更新线程"
    stop_update.short_description = "停止更新线程"
    actions = [start_update, stop_update]


@admin.register(Template)
class TemplateAdmin(BaseAdmin):
    list_display = ['id', 'name', 'type', 'nickname']
    fields = ['name', 'nickname', 'type', 'content']


@admin.register(SubLog)
class SubLogAdmin(BaseAdmin):
    list_display = ['id', 'user', 'user_nickname', 'client', 'ip']
    fields = ['user', 'client', 'ip']

    def user_nickname(self, obj):
        if obj.user:
            return obj.user.nickname
        return None

    user_nickname.short_description = '昵称'


@admin.register(Files)
class FilesAdmin(BaseAdmin):
    list_display = ['id', 'name', 'url', 'path', 'interval', 'autoupdate']
    fields = ['name', 'autoupdate', 'url', 'path', 'interval']


@admin.register(Repo)
class RepoAdmin(BaseAdmin):

    def start_update(self, request, queryset):
        try:
            skips, success = [], []
            for repo in queryset:
                if repo.id in configs._repo_thrds:
                    _th: UpdateRepoThread = configs._repo_thrds[repo.id]
                    if _th.is_alive():
                        skips.append(repo.name)
                        continue
                    else:
                        del _th
                _th = UpdateRepoThread(repo)
                _th.start()
                configs._repo_thrds[repo.id] = _th
                success.append(repo.name)
            s1 = ",".join(skips[:3])
            s2 = ",".join(success[:3])

            messege = f"成功启动：{s2}等，已跳过:{s1}"

            self.message_user(request, "操作成功", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"失败:{e}", messages.ERROR)

    def stop_update(self, request, queryset):
        try:
            for repo in queryset:
                if repo.id not in configs._repo_thrds:
                    continue
                _th: UpdateRepoThread = configs._repo_thrds[repo.id]
                _th.kill()
                del configs._repo_thrds[repo.id]

            self.message_user(request, "操作成功", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"失败:{e}", messages.ERROR)

    start_update.short_description = "启动更新线程"
    stop_update.short_description = "停止更新线程"
    actions = [start_update, stop_update]

    list_display = ['id', 'name','branch', 'url', 'path', 'interval', 'version', 'up_thred_status', 'autoupdate']
    fields = ['name','branch', 'autoupdate', 'url', 'path', 'interval', 'version']
