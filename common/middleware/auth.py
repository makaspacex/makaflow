#! /usr/bin/python
# -*- coding: utf-8 -*-
# @author izhangxm
# @date 2021/4/15
# @fileName page_const.py
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
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from Makaflow import urls


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request: WSGIRequest):
        _need_auth = urls.home_need_auth
        path = request.path
        path = path[1:] if path.startswith("/") else path

        need_verify_login = False
        for urlp in _need_auth:
            match = urlp.pattern.match(path)
            if match:
                need_verify_login = True
                break
        setattr(request, "_dont_enforce_csrf_checks", True)
        if not need_verify_login:
            return None

        if request.session.get("user", None):
            return None

        if not request.is_ajax():
            return redirect("/page/auth/signin")
        else:
            return JsonResponse({"status": 0, "info": "need to login"})

        # if (not path.startswith('/admin'))  and (not path.startswith('/simplepro'))

    def process_response(self, request: WSGIRequest, response: HttpResponse):
        if "page" in request.path.split("/"):
            pass
        return response
