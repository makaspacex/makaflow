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
from django.http import HttpRequest
from apps.makaflow import configs
from apps.makaflow import urls as app_urls


def is_ajax(request):
    a = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    return bool(a or request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('_ajax'))

class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):
        path = request.path
        path = path[1:] if path.startswith("/") else path
        
        for urlp in app_urls.need_rpckey:
            match = urlp.pattern.match(path)
            if not match:
                continue
            message = None
            auth  = request.headers.get("rpckey", None)
            env = configs.env
            rpc = str(env["rpc_key"])
            if auth is None:
                message = "rpckey header is none"
            elif rpc != auth:
                message =  "rpc key error"
            
            if message is not None:
                return JsonResponse({"status": 0, "info": f"{message}"})
        
        return None

    def process_response(self, request: WSGIRequest, response: HttpResponse):
        if "page" in request.path.split("/"):
            pass
        return response