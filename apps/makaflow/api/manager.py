import mimetypes
import os
from glob import glob
from pathlib import Path

import requests
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseNotFound, FileResponse

from apps.makaflow import configs
from apps.makaflow import tools
from apps.makaflow.models import Template
from apps.makaflow.tools import geo
from apps.makaflow.tools import subscrib_xray, get_request_client
from apps.makaflow.tools.common import ClientApp
from apps.makaflow.tools.convert_api import xj_rule_convert
from common.models import Config
from common.models import XJUser as User
import re
from apps.makaflow.tasks import load_all


def api_subscrib_v1(request: HttpRequest):
    # 返回用户的的订阅，需要检查用户名和密码，和客户端，clash_verge 支持吃v2的tls
    resp_data = tools.get_default_resp_data()
    try:
        token = request.GET.get("token", None)
        client_type = get_request_client(request=request)

        if not token:
            raise Exception("miss token")

        user = User.objects.filter(token=token).first()
        if not user:
            raise Exception("user not found")
        if user.level < 0:
            raise Exception(f"id:{user.username} nickname:{user.nickname} is disabled")

        resp_txt, resp_headers = subscrib_xray.render_tp(user, client_type=client_type)
        resp = HttpResponse(resp_txt)
        for hname, hvalue in resp_headers.items():
            resp.headers[hname] = hvalue
        resp.headers["content-type"] = "text/plain; charset=utf-8"
        return resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return JsonResponse(resp_data)


def api_generate_config(request: HttpRequest, service):
    # 更新服务器参数
    resp_data = tools.get_default_resp_data()
    try:
        tools.serverconfig.update(service)
    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return JsonResponse(resp_data)


def api_push_config(request: HttpRequest):
    # 推送配置到远程节点
    resp_data = tools.get_default_resp_data()
    try:
        resp = tools.serverconfig.push_config()
        resp_data["data"] = resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return JsonResponse(resp_data)


def api_push_service_op(request: HttpRequest, op):
    resp_data = tools.get_default_resp_data()
    try:
        nodes = configs.env["slaver"]["nodes"]
        data = {}

        for node_name, node_conf in nodes.items():
            try:
                api_base = node_conf["api_base"]
                rpc_key = node_conf["rpc_key"]
                enabled = node_conf["enable"]
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
    return JsonResponse(resp_data)


def api_get_service_status(request: HttpRequest):
    resp_data = tools.get_default_resp_data()
    try:
        nodes = configs.env["slaver"]["nodes"]
        data = {}

        for node_name, node_conf in nodes.items():

            try:
                api_base = node_conf["api_base"]
                rpc_key = node_conf["rpc_key"]
                enabled = node_conf["enable"]
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
    return JsonResponse(resp_data)


def api_rule(request: HttpRequest, client, code, suffix):
    resp_data = tools.get_default_resp_data()
    try:
        content = ""
        if client == "clash":
            content = geo.clash_rules(
                geosites=configs.geosites, geoips=configs.geoips, country_code=code
            )
        elif client.lower() in ["loon", "surge"]:
            content = geo.loon_surge_rules(
                geosites=configs.geosites, geoips=configs.geoips, country_code=code
            )

        resp = HttpResponse(content)
        resp.headers["content-type"] = "text/plain; charset=utf-8"
        return resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return JsonResponse(resp_data)


def api_mix_file_download(request: HttpRequest, path):
    resp_data = tools.get_default_resp_data()
    try:
        client_type = get_request_client(request=request)
        path = Path(path)
        rule_repo_dir = Path(Config.get("resource_dir", default="runtime/mixrule"))
        finale_file_path = rule_repo_dir / path

        rule_mode = False
        if "mixrule/" in request.path:
            rule_mode = True
            if not finale_file_path.exists():
                flist = glob(
                    str(finale_file_path.parent / finale_file_path.stem) + ".*"
                )
                if len(flist) == 0:
                    return HttpResponseNotFound()
                finale_file_path = Path(flist[0])
        elif "data/icon" in request.path:
            finale_file_path = path
        
        if not finale_file_path.exists():
            return HttpResponseNotFound()

        if rule_mode:
            # 处理规则
            with open(finale_file_path, "r") as f:
                f_content = f.read()
            # client_type 强制覆盖
            if client_type == ClientApp.surfboard:
                client_type = ClientApp.surge
            if client_type in ClientApp.clashmeta_group + ClientApp.clash_group:
                client_type = ClientApp.clash

            if client_type in [ClientApp.browser]:
                content = f_content
            elif client_type in ClientApp.sub_store_support:
                content = xj_rule_convert(f_content, client_type)
            else:
                raise Exception("未知的客户端类型")

            resp = HttpResponse(content)
            resp.headers["content-type"] = "text/plain; charset=utf-8"
            return resp
        elif re.search(r"api/iconset/.*?.json", request.path, flags=re.IGNORECASE):
            _r = re.search(r"api/iconset/.*?.json", request.path, flags=re.IGNORECASE)
            with open(finale_file_path, "r") as f:
                f_content = f.read()
            icon_base_url = Config.get(
                "icon_base_url", "https://cat.makafly.com/api/icon"
            )
            re_p = re.compile(
                r'"https://raw.githubusercontent.com/.*?/(.*?)/.*?/(.*?)"'
            )
            repl_p = '"' + icon_base_url + r'/\1/\2"'
            content = re_p.sub(repl_p, f_content)
            resp = HttpResponse(content)
            resp.headers["content-type"] = "text/json; charset=utf-8"
            return resp

        else:
            content_type, encoding = mimetypes.guess_type(finale_file_path)
            if content_type and content_type.startswith("text/") and encoding is None:
                content_type += "; charset=utf-8"
            return FileResponse(open(finale_file_path, "rb"), content_type=content_type)

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return JsonResponse(resp_data)


def api_loon_conf(request: HttpRequest, conf):
    resp_data = tools.get_default_resp_data()
    try:
        token = request.GET.get("token", None)
        if not token:
            raise Exception("miss token")
        user = User.objects.filter(token=token).first()
        if not user:
            raise Exception("user not found")
        if user.level < 0:
            raise Exception(f"id:{user.username} nickname:{user.nickname} is disabled")

        tp_name = "loon_tp"
        tp = Template.objects.filter(name=tp_name).first()

        resp = HttpResponse()
        resp.headers["content-type"] = "text/plain; charset=utf-8"
        if not tp:
            resp.status_code = 404
            resp.content = f"没有发现名称为{tp_name}的Loon配置模板"
            return resp
        content = tp.content
        content = content.replace(
            "api/v1/client/subscribe?token=123456",
            f"api/v1/client/subscribe?token={token}",
        )
        resp.content = content
        return resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return JsonResponse(resp_data)


def api_loadall(request: HttpRequest):
    resp_data = tools.get_default_resp_data()
    try:
        load_all()
    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return JsonResponse(resp_data)
