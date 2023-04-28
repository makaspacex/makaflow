#! /usr/bin/python
# -*- coding: utf-8 -*-
# @author izhangxm
# @date 2021/4/16
# @fileName query_tools.py
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
from common.config import NULL_STR
from common.tools.model_tools import get_model_field_info


def get_where_map(q_list: dict, dj_model):
    fields_info = get_model_field_info(dj_model)

    ret = {}
    for k, v in q_list.items():
        k = str(k)
        v = str(v)
        if not k.startswith('_where_'):
            continue
        if v == '':
            continue
        n_k = k.split('_where_')[-1]

        if n_k == 'ctime_start':
            continue

        if n_k == 'ctime_end':
            continue

        field_info = fields_info.get(n_k)
        if not field_info:
            continue

        from_name = field_info['from_name']
        field_type = field_info['field_type']
        real_name = field_info['real_name']

        where_name = f"{from_name}__{real_name}" if from_name != '' else f"{real_name}"
        if field_type in ['IntegerField', 'BigIntegerField', 'AutoField']:
            if '-' in v:
                s = int(v.split('-')[0])
                e = int(v.split('-')[1])
                ret[where_name + '__gte'] = s
                ret[where_name + '__lte'] = e
            else:
                ret[where_name] = v
        elif field_type in ['CharField', 'TextField']:
            # 处理空字符串
            if v == NULL_STR:
                ret[where_name + '__isnull'] = True
                continue
            ret[where_name + "__contains"] = v
    return ret


if __name__ == '__main__':
    from MediaAI.models import DBPics

    print(get_where_map({'_where_age': 12, '_where_picture__pic_id': 'zhangsan', '_where_dataset_id': 'datasetid'},
                        DBPics))
