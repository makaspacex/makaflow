#! /usr/bin/python
# -*- coding: utf-8 -*-
# @author izhangxm
# @date 2021/12/3
# @fileName common.py
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
from django.contrib import auth

from common import config
from common.models import XJUser
from common.tools import model_tools


def const_vars(request):
    if request.is_ajax():
        return None
    user_model: XJUser = auth.get_user_model()
    user_id = request.session.get('_auth_user_id')
    user = user_model.objects.filter(id=user_id).first()
    if user:
        user = model_tools.get_json_model(user)
    else:
        user = {}

    context = {
        'NULL_STR': config.NULL_STR,
        'AUTH_KEY_PREFIX': config.AUTH_KEY_PREFIX,
        'ip_address': request.META['REMOTE_ADDR'],
        'login_user': user
    }
    return context
