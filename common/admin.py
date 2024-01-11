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

import types

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  # 从django继承过来后进行定制
from django.contrib.auth.models import Permission
from import_export.admin import ImportExportActionModelAdmin
from simpleui.admin import AjaxAdmin

from .models import *

# 修改网页title和站点header。
admin.site.site_title = "后台管理"
admin.site.site_header = "后台管理"
LIST_PER_PAGE_DEFAULT = 20


class BaseAdmin(AjaxAdmin, ImportExportActionModelAdmin):
    list_per_page = LIST_PER_PAGE_DEFAULT
    auto_time_fields = ['created_at', 'updated_at']
    status_fields = ['status']

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        # print(f"{self.__class__.__name__} {'*' * 20}")
        cls = self.__class__

        dynamic_actions = getattr(self, 'dynamic_actions', None)
        if dynamic_actions is not None:
            def get_actions(self, request):
                _su = super().get_actions(request)
                for fn in dynamic_actions:
                    if not callable(fn):
                        continue
                    _action = fn()
                    _su[fn.__name__] = (_action, fn.__name__, getattr(_action, 'short_description', None))
                    setattr(cls, fn.__name__, _action)
                    # print("haha+++++")

                return _su

            setattr(cls, 'get_actions', types.MethodType(get_actions, self))

        def _get_admin_attr(cls, name):
            _a = getattr(cls, name, [])
            res = list(_a) if _a is not None else []
            return res

        cls.list_display = _get_admin_attr(cls, 'list_display') + cls.auto_time_fields + cls.status_fields
        cls.list_filter = _get_admin_attr(cls, 'list_filter') + cls.auto_time_fields + cls.status_fields

        if not getattr(cls, 'no_auto_fields', False):
            cls.fields = _get_admin_attr(cls, 'fields') + cls.auto_time_fields + cls.status_fields
        cls.readonly_fields = _get_admin_attr(cls, 'readonly_fields') + cls.auto_time_fields
        cls.list_editable = _get_admin_attr(cls, 'list_editable') + cls.status_fields

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(XJUser)
class XJUserAdmin(BaseAdmin, UserAdmin):
    list_display = ['username','nickname', 'level', 'email', 'is_staff', 'is_active', 'user_group_display',
                    'is_superuser']
    readonly_fields = ['date_joined', 'last_login']
    
    no_auto_fields = True
    
    _add_and_edit_fields = ['nickname', 'level', 'email', 'token','uuid', 'is_active', 'is_staff',
                             'is_superuser']
    
    add_fieldsets = [
        ("个人信息", {'fields': ['username', 'password1', 'password2'] +  _add_and_edit_fields + BaseAdmin.auto_time_fields}),
    ]

    fieldsets = [
        ("个人信息", {'fields': ['username', 'password'] + _add_and_edit_fields + BaseAdmin.auto_time_fields}),
    ]

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets

        # 超级管理员不需要设置权限
        if obj.is_superuser:
            return self.fieldsets
        # 普通管理员需要设置权限和分组
        if obj.is_staff:
            return self.fieldsets + [('权限', {'fields': ['groups', 'user_permissions']})]
        return self.fieldsets


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'content_type', 'codename']
    list_per_page = LIST_PER_PAGE_DEFAULT
