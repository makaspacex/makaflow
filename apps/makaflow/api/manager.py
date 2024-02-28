import json
import os
from argparse import ArgumentParser, Namespace
from copy import deepcopy
from io import StringIO
from pathlib import Path
from django.http import StreamingHttpResponse
import numpy as np
import requests
from pathlib import Path
from apps.makaflow import configs
from apps.makaflow import tools
from apps.makaflow.tools import common, subscrib, subscrib_xray, get_request_client
from apps.makaflow.tools.common import ClientApp, yaml
from django.http.response import HttpResponse
from django.http.request import HttpRequest
from django.http import JsonResponse
from apps.makaflow.tools import geo
from apps.makaflow.tools.convert_api import xj_rule_convert


def api_subscrib_old(request:HttpRequest):
    # 返回用户的的订阅，需要检查用户名和密码，和客户端，clash_verge 支持吃v2的tls
    resp_data = tools.get_default_resp_data()
    try:
        username = request.GET.get("uname", None)
        password = request.GET.get("password", None)
        
        client_type = get_request_client(request=request)

        if not username or not password:
            raise Exception("miss uname or password ")

        users = configs.users

        users_dict = {ele["name"]: ele for ele in users}
        if username not in users_dict.keys():
            raise Exception("user not found")

        user_auth = users_dict[username]["auth"]
        assert user_auth == password, "password mismatch"
        
        # 用户详细信息
        user = users_dict[username]
        
        # clashmeta_config = subscrib_xray.render_tp(username, client_type=client_type)
        resp_txt, resp_headers = subscrib_xray.render_tp( user, client_type=client_type)
        resp = HttpResponse(resp_txt)
        for hname, hvalue in resp_headers.items():
            resp.headers[hname] = hvalue
        resp.headers["content-type"] = "text/yaml; charset=utf-8"
        
        return resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return JsonResponse(resp_data)


def api_subscrib_v1(request:HttpRequest):
    # 返回用户的的订阅，需要检查用户名和密码，和客户端，clash_verge 支持吃v2的tls
    resp_data = tools.get_default_resp_data()
    try:
        token = request.GET.get("token", None)
        client_type = get_request_client(request=request)
        
        if not token:
            raise Exception("miss token")

        users = configs.users
        token_dict = {ele["token"]: ele for ele in users}

        if token not in token_dict.keys():
            raise Exception("user not found")
        
        # 用户详细信息
        user = token_dict[token]
        
        if user['level'] < 0:
            raise Exception(f"id:{user['name']} nickname:{user['nickname']} is disabled")
        
        # clashmeta_config = subscrib_xray.render_tp(username, client_type=client_type)
        resp_txt, resp_headers = subscrib_xray.render_tp( user, client_type=client_type)
        resp = HttpResponse(resp_txt)
        for hname, hvalue in resp_headers.items():
            resp.headers[hname] = hvalue
        resp.headers["content-type"] = "text/yaml; charset=utf-8"
        
        return resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
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

def api_rule(request:HttpRequest, client, code, suffix):
    resp_data = tools.get_default_resp_data()
    try:
        content = ""
        if client == 'clash':
            content = geo.clash_rules(geosites=configs.geosites, geoips=configs.geoips, country_code=code)
        elif client.lower() in ['loon','surge']:
            content = geo.loon_surge_rules(geosites=configs.geosites, geoips=configs.geoips, country_code=code)
        
        resp = HttpResponse(content)
        resp.headers["content-type"] = "text/yaml; charset=utf-8"
        return resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)

from pathlib import Path
def api_mixrule(request:HttpRequest, path):
    resp_data = tools.get_default_resp_data()
    try:
        client_type = get_request_client(request=request)
        path = Path(path)
        
        rule_repo_dir = Path(configs.env['rule_repo_dir']) 
        finale_file_path = rule_repo_dir / path
        if not finale_file_path.exists():
            # 不存在则寻找同名文件
            from glob import glob
            flist = glob( str(finale_file_path.parent / finale_file_path.stem) + '.*' )
            if len(flist) == 0:
                raise Exception(f"Not Found {path}")
            finale_file_path = flist[0]
        
        with open(finale_file_path, 'r') as f:
            f_content = f.read()
        
        content = ""
        # # 后缀名判断
        # if path.suffix == '.yaml':
        #     client_type = ClientApp.clash
        # if path.suffix == '.list':
        #     client_type = ClientApp.surge
        
        # clienttype 强制覆盖
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
    
    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)


def api_rule_bm7(request:HttpRequest, path:str):
    resp_data = tools.get_default_resp_data()
    try:
        
        blackmatrix7_rule_dir = os.path.join(configs.env['rule_repo_dir'], "ios_rule_script/rule")
        
        f_path = os.path.join(blackmatrix7_rule_dir, path)
        resp = HttpResponse()
        resp.headers["content-type"] = "text/plain; charset=utf-8"
        if not os.path.exists(f_path):
            resp.status_code = 404
            resp.content = f"404: {path} not found"
            return resp
        with open(f_path, 'r') as f:
            content = f.read()
            resp.content = content
        return resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)

def api_conf(request:HttpRequest, conf):
    resp_data = tools.get_default_resp_data()
    try:
        token = request.GET.get("token", None)
        if not token:
            raise Exception("miss token")
        users = configs.users
        token_dict = {ele["token"]: ele for ele in users}
        if token not in token_dict.keys():
            raise Exception("invalid token")
        
        subscribe_tp_dir = configs.env['subscribe_tp_dir']
        f_path = os.path.join(subscribe_tp_dir, conf)
        resp = HttpResponse()
        resp.headers["content-type"] = "text/yaml; charset=utf-8"
        if not os.path.exists(f_path):
            resp.status_code = 404
            resp.content = f"404: {conf} not found"
            return resp
        with open(f_path, 'r') as f:
            content = f.read()
            content = content.replace("api/v1/client/subscribe?token=123456",f"api/v1/client/subscribe?token={token}")
            resp.content = content
        return resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)

def file_iterator(file_path, chunk_size=512):
    with open(file_path, mode='rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break

def get_file_resp(f_path):
    
    if not os.path.exists(f_path):
        resp = HttpResponse()
        resp.status_code = 404
        resp.headers["content-type"] = "text/yaml; charset=utf-8"
        resp.content = f"404: not found"
        return resp
    b_name = os.path.basename(f_path)
    response = StreamingHttpResponse(file_iterator(f_path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = f'attachment;filename="{b_name}"'
    return response

def api_resource_down(request:HttpRequest, path):
    resp_data = tools.get_default_resp_data()
    try:
        resource_dir = configs.env['resource_dir']
        f_path = os.path.join(resource_dir, path)
        resp = get_file_resp(f_path=f_path)
        return resp
    
    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)

def api_icon(request:HttpRequest, path):
    resp_data = tools.get_default_resp_data()
    try:
        icon_repo_dir = configs.env['icon_repo_dir']
        f_path = os.path.join(icon_repo_dir, path)
        resp = get_file_resp(f_path=f_path)
        return resp
    
    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)


from apps.makaflow.tasks import load_all
def api_loadall(request:HttpRequest):
    resp_data = tools.get_default_resp_data()
    try:
        load_all()
    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return  JsonResponse(resp_data)

