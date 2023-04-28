#! /usr/bin/python
# -*- coding: utf-8 -*-
# @author izhangxm
# @date 2021/4/19
# @fileName public.py
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

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from common.tools.UUID import get_uid


def get_auth_key(request: WSGIRequest):
    resp_data = {"code": 1, "info": "ok"}
    try:
        resp_data['data'] = get_uid().upper()
    except Exception as e:
        resp_data['code'] = 0
        resp_data['info'] = 'Failed: ' + str(e)
    return JsonResponse(resp_data)

