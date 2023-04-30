import json
import os
from argparse import ArgumentParser, Namespace
from copy import deepcopy
from io import StringIO
from pathlib import Path

import flask
import numpy as np
import requests
from flask import Flask, request

from apps.makaflow import configs
from apps.makaflow import tools
from apps.makaflow.tools import common, subscrib, subscrib_xray
from apps.makaflow.tools.common import ClientApp, yaml
from apps.makaflow.tools.subscrib_common import start_tasks
from django.http.response import HttpResponse
from django.http.request import HttpRequest
from django.http import JsonResponse


# 节点本身的操作
def api_service_op(request:HttpRequest, op):
    resp_data = tools.get_default_resp_data()
    try:
        res1 = tools.service_op(op, "sing-box")
        res2 = tools.service_op(op, "xray")

        resp_data["data"] = f"singbox:ok xray:ok"

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)


# 节点本身的操作
def api_server_log(request:HttpRequest,service):
    # parame: last_rows  default 300
    # 应该要实时返回用户的日志, 默认返回最新的300条数据
    resp_data = tools.get_default_resp_data()
    try:
        server_profile = tools.load_server_profile(service)
        log_path = server_profile["log"]["output"]
        with open(log_path, "r") as f:
            lines = f.readlines()

        last = min(len(lines), 300)
        out_str = "\n".join(lines[-last:])

        return out_str

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)


# 节点本身的操作
def api_server_config(request:HttpRequest,service):
    # API接口 返回本服务器的相关配置的一些信息，需要验证统一的key
    resp_data = tools.get_default_resp_data()
    try:
        server_profile = tools.load_server_profile(service)
        config_json = tools.load_server_config(
            config_json_path=server_profile["dst_server_cfg"]
        )
        return config_json
    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)


def api_user_state(request:HttpRequest):
    # TODO 查看服务状态和用户状态，流量等
    resp_data = tools.get_default_resp_data()
    try:
        state1 = tools.get_service_state("sing-box")
        state2 = tools.get_service_state("xray")

        data = {"service": f"singbox:{state1} xray:{state2}"}
        resp_data["data"] = data

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)


def api_update_config(request:HttpRequest):
    # 接收配置
    resp_data = tools.get_default_resp_data()
    try:
        xray_config = request.form.get("xray_config", "{}")
        singbox_config = request.form.get("singbox_config", "{}")

        xray_config = json.loads(xray_config)
        singbox_config = json.loads(singbox_config)

        common.dump_server_config(
            xray_config,
            configs.env[f"xray_server_cfg"],
        )
        common.dump_server_config(
            singbox_config,
            configs.env[f"singbox_server_cfg"],
        )
        resp_data["data"] = f"xray:ok singbox:ok"

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
        raise e
    return  JsonResponse(resp_data)

