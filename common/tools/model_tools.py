#! /usr/bin/python
# -*- coding: utf-8 -*-
# @author izhangxm
# @date 2021/4/18
# @fileName model_tools.py
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
# import __initDjangoEnvironment

from inspect import isfunction

import pytz
from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.db.models import query_utils
from django.db.models.fields.files import FieldFile
from django.db.models.fields.related import ForeignKey
from django.utils import timezone


def get_model_field_info_old(dj_model, field_info_base=None, from_name=''):
    if field_info_base is None:
        field_info_base = {}
    all_attrs = vars(dj_model)
    # all_attr_names = dir(dj_model)

    # 先处理本类的普通字段，用来防止被子表的相同的字段覆盖
    for name, obj in all_attrs.items():
        # for name in all_attr_names:
        #     obj = getattr(dj_model, name)
        if not hasattr(obj, '__class__') or name.startswith('_'):
            continue
        cl_name = obj.__class__.__name__
        if cl_name in ['ForeignKeyDeferredAttribute']:
            # 外间自动生成的对应的字段域，是属于本类的基础字段域
            column_name = obj.field.get_attname()
            field_type = obj.field.related_fields[0][-1].__class__.__name__
            f_info = {'from_name': from_name, 'field_type': field_type, 'belong_model': dj_model,
                      'real_name': column_name}
            if from_name == '':
                field_info_base[f"{column_name}"] = f_info
            else:
                field_info_base[f"{from_name}__{column_name}"] = f_info
                if column_name not in field_info_base:
                    field_info_base[f"{column_name}"] = f_info

        elif hasattr(obj, "__module__") and obj.__module__ == query_utils.__name__:
            # 直接定义的普通字段域
            f_info = {'from_name': from_name, 'field_type': obj.field.__class__.__name__, 'belong_model': dj_model,
                      'real_name': name}
            if from_name == '':
                field_info_base[f"{name}"] = f_info
            else:
                field_info_base[f"{from_name}__{name}"] = f_info
                if name not in field_info_base:
                    field_info_base[f"{name}"] = f_info
        elif isfunction(obj):
            # 直接定义的普通字段域
            f_info = {'from_name': from_name, 'field_type': obj.__class__, 'belong_model': dj_model,
                      'real_name': name}
            if from_name == '':
                field_info_base[f"{name}"] = f_info
            else:
                field_info_base[f"{from_name}__{name}"] = f_info
                if name not in field_info_base:
                    field_info_base[f"{name}"] = f_info

    # 再处理子表的外间字段
    for name, obj in all_attrs.items():
        # for name in all_attr_names:
        #     obj = getattr(dj_model, name)
        if not hasattr(obj, '__class__') or name.startswith('__'):
            continue
        cl_name = obj.__class__.__name__
        if cl_name in ['ForwardManyToOneDescriptor'] and from_name == '':
            # 首先判断是不是外键，外间的判断不可以用field来判断，因为自动生成的db_column也显示为外间
            # 而且不在递归子表的外间，防止出现循环引用，无限递归
            obj_field: ForeignKey = obj.field
            model_obj = obj_field.related_model  # 外间的模型类
            get_model_field_info(model_obj, field_info_base=field_info_base, from_name=name)

    return field_info_base


def get_model_field_info(dj_model, field_info_base=None, from_name=''):
    if field_info_base is None:
        field_info_base = {}

    if not isinstance(dj_model, models.base.ModelBase):
        raise Exception('not django model')
    if not hasattr(dj_model, '_meta'):
        raise Exception('have no attr: _meta')

    concrete_model = dj_model._meta.concrete_model
    all_fields = concrete_model._meta.local_fields

    # 先处理本类的普通字段，用来防止被子表的相同的字段覆盖
    for field in all_fields:
        column_name = field.attname
        field_type = field.model.__name__
        f_info = {'from_name': from_name, 'field_type': field_type, 'belong_model': dj_model, 'real_name': column_name}
        key_name = f"{column_name}" if from_name == '' else f"{from_name}__{column_name}"
        field_info_base[key_name] = f_info

    all_attrs = vars(dj_model)
    for name, obj in all_attrs.items():
        if not hasattr(obj, '__class__') or name.startswith('_'):
            continue
        if isfunction(obj):
            # 直接定义的普通字段域
            f_info = {'from_name': from_name, 'field_type': obj.__class__, 'belong_model': dj_model, 'real_name': name}
            key_name = f"{name}" if from_name == '' else f"{from_name}__{name}"
            field_info_base[key_name] = f_info

    # 再处理子表的外间字段
    for field in all_fields:
        if not isinstance(field, ForeignKey):
            continue
        fname = field.name
        if from_name:
            fname = f"{from_name}__{fname}"
        model_obj = field.related_model().__class__
        get_model_field_info(model_obj, field_info_base=field_info_base, from_name=fname)

    return field_info_base


def get_json_model(object_s, datetime_format="%Y-%m-%d %H:%M:%S"):
    def model_inst_dumps(obj):
        result = {}
        try:
            if isinstance(obj, dict):
                return obj
            if not hasattr(obj, '__class__') or isinstance(obj.__class__.__base__, models.Model):
                return None
            fields_info = get_model_field_info(obj.__class__)

            for name, field_info in fields_info.items():
                real_name = field_info['real_name']
                from_name = field_info['from_name']
                if from_name != '':
                    fnames = from_name.split('__')
                    value = getattr(obj, fnames[0])
                    if len(fnames)>1:
                        for fname in fnames[1:]:
                            value = getattr(value, fname)
                    value = getattr(value, real_name)
                else:
                    value = getattr(obj, real_name)
                try:
                    if hasattr(value, '__call__'):
                        value = value()
                except Exception as e:
                    raise e
                if isinstance(value, timezone.datetime):
                    value = value.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(datetime_format)
                if isinstance(value, FieldFile):
                    try:
                        result[f"{name}__download_url"] = value.url
                    except Exception:
                        result[f"{name}__download_url"] = None
                if not isinstance(value, int):
                    value = str(value)
                result[name] = value

        except Exception as e:
            raise e
        return result

    if isinstance(object_s, QuerySet):
        results = []
        for m_inst in object_s:
            results.append(model_inst_dumps(m_inst))
        return results

    return model_inst_dumps(object_s)


def get_update_map(form_data, dj_model):
    fields_info = get_model_field_info(dj_model)
    ret = {}
    for k, v in form_data.items():
        k = str(k)
        v = str(v)
        if v and k in fields_info and v != '':
            ret[k] = v
    return ret


if __name__ == '__main__':
    from apps.testingsystem.models import DBPics

    aa = get_model_field_info(DBPics)

    print(aa)
