import json
import os
from argparse import ArgumentParser, Namespace
from copy import deepcopy
from io import StringIO
from pathlib import Path

import flask
import numpy as np
import requests

from apps.makaflow import configs
from apps.makaflow import tools
from apps.makaflow.tools import common, subscrib, subscrib_xray
from apps.makaflow.tools.common import ClientApp, yaml
from apps.makaflow.tools.subscrib_common import start_tasks
from django.http.response import HttpResponse
from django.http.request import HttpRequest
from django.http import JsonResponse


def api_subscrib(request:HttpRequest):
    # 返回用户的的订阅，需要检查用户名和密码，和客户端，clash_verge 支持吃v2的tls
    resp_data = tools.get_default_resp_data()
    try:
        username = request.GET.get("uname", None)
        password = request.GET.get("password", None)
        client_type = request.GET.get("client", None)

        if client_type is None:
            user_agent = request.headers.get("User-Agent", "").lower()
            if "shadowrocket" in user_agent:
                client_type = ClientApp.shadowrocket

            # clash meta内核
            elif "clash-verge" in user_agent or "ClashX Meta" in user_agent:
                client_type = ClientApp.clashmeta

            # 含有clash关键字，但是不能有clash-verge
            elif "clash" in user_agent and "clash-verge" not in user_agent:
                client_type = ClientApp.clash

            elif "loon" in user_agent:
                client_type = ClientApp.loon
            elif "Stash" in user_agent:
                client_type = ClientApp.stash
            else:
                client_type = ClientApp.browser

        if not username or not password:
            raise Exception("miss uname or password ")

        users = configs.users

        users_dict = {ele["name"]: ele for ele in users}
        if username not in users_dict.keys():
            raise Exception("user not found")

        user_auth = users_dict[username]["auth"]
        assert user_auth == password, "password mismatch"

        # clashmeta_config = subscrib_xray.render_tp(username, client_type=client_type)
        resp_txt, resp_headers = subscrib_xray.render_tp(
            username, client_type=client_type
        )
        resp = HttpResponse(resp_txt)
        for hname, hvalue in resp_headers.items():
            resp.headers[hname] = hvalue
        resp.headers["content-type"] = "text/yaml; charset=utf-8"
        
        return resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
        raise e
    return JsonResponse(resp_data)

def api_generate_config(request:HttpRequest, service):
    # 更新服务器参数
    resp_data = tools.get_default_resp_data()
    try:
        tools.serverconfig.update(service)
    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return JsonResponse(resp_data)

def api_push_config(request:HttpRequest):
    # 推送配置到远程节点
    resp_data = tools.get_default_resp_data()
    try:
        resp = tools.serverconfig.push_config()
        resp_data["data"] = resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return JsonResponse(resp_data)

def api_push_service_op(request:HttpRequest, op):
    resp_data = tools.get_default_resp_data()
    try:
        nodes = configs.env["slaver"]["nodes"]
        data = {}

        for node_name, node_conf in nodes.items():
            try:
                api_base = node_conf["api_base"]
                rpc_key = node_conf["rpc_key"]
                enabled = node_conf['enable']
                if not enabled:
                    continue

                push_api_url = f"{api_base}/serverop/{op}"
                resp = requests.get(push_api_url, headers={"rpckey": rpc_key})
                if resp.status_code != 200:
                    raise Exception(resp.reason)
                data[node_name] = resp.json()
            except Exception as e:
                data[node_name] = f"failed: {e}"

        resp_data["data"] = data

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)

def api_get_service_status(request:HttpRequest):
    resp_data = tools.get_default_resp_data()
    try:
        nodes = configs.env["slaver"]["nodes"]
        data = {}

        for node_name, node_conf in nodes.items():
            
            try:
                api_base = node_conf["api_base"]
                rpc_key = node_conf["rpc_key"]
                enabled = node_conf['enable']
                if not enabled:
                    continue
                
                push_api_url = f"{api_base}/serverstate"
                resp = requests.get(push_api_url, headers={"rpckey": rpc_key})
                if resp.status_code != 200:
                    raise Exception(resp.reason)
                data[node_name] = resp.json()

            except Exception as e:
                data[node_name] = f"failed: {e}"

        resp_data["data"] = data

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)
