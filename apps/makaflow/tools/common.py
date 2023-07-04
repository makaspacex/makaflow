import json
import subprocess
import time
import ruamel.yaml
from base64 import b64encode
from secrets import token_bytes
from copy import deepcopy
import numpy as np
from io import StringIO 
import base64
import x25519
import os
from apps.makaflow import configs
import urllib
import re
import copy
from django.http.request import HttpRequest
from dataclasses import dataclass

yaml = ruamel.yaml.YAML()

@dataclass
class ClientApp:
    clash:str = "Clash" # clash 各个平台的clash，如安卓，widows和软路由, 包含premium版本, 后期有需要再细分
    stash:str = "Stash"
    
    surge:str = "Surge"
    qx:str = "QX"
    
    # 支持更高级的功能和语法，优先支持    
    clashmeta:str = "clashmeta" # clashmeta内核的一切软件
    
    # 它们只需要分享链接式的配置
    loon:str = "Loon"
    shadowrocket:str = "Shadowrocket"
    singbox:str = "singbox" # singbox 内核的一切软件
    xray:str = "xray" # xray 内核的一切软件
    browser:str = "browser"
    
    # sub_store_support = ["QX", "Surge", "Loon","Clash","URI","JSON","Stash"]
    sub_store_support = [qx, surge, loon, stash]

    clash_group = [clash,stash]
    clashmeta_group = [clashmeta]
    sharelink_group= [loon, shadowrocket, singbox, xray, browser]

def get_request_client(request:HttpRequest):
    client_type = request.GET.get("client", None)
    
    if client_type is None:
        user_agent = request.headers.get("User-Agent", "").lower()
        if "shadowrocket" in user_agent:
            client_type = ClientApp.shadowrocket
        # clash meta内核
        elif "clash-verge" in user_agent or "ClashX Meta" in user_agent:
            client_type = ClientApp.clashmeta
        elif "Stash".lower() in user_agent:
            client_type = ClientApp.stash
        # 含有clash关键字，托底的clash
        elif "clash" in user_agent:
            client_type = ClientApp.clash
        elif "loon".loer() in user_agent:
            client_type = ClientApp.loon
        else:
            client_type = ClientApp.browser
    else:
        attrs = ClientApp.__annotations__
        for name, tp in attrs.items():
            va = getattr(ClientApp, name)
            if not isinstance(va, str):
                continue
            if client_type.lower() == va.lower():
                client_type = va
    
    return client_type


def proxy_process(node_name, node_conf, proxy:dict):
    
    proxy = copy.deepcopy(proxy)
    
    exclude_node = node_conf.get("exclude_node", None)
    name_prefix_str = node_conf.get("prefix","")
    repl_names = node_conf.get("repl_names", [])
    server_mirr_dict = {ele['ori']:ele['mirr'] for ele in node_conf.get('server_mirr', [])}
    
    # 处理过滤节点
    if exclude_node:
        _r = re.search(exclude_node, proxy['name'])
        if _r:
            return None
    
    # 节点名字去空格
    proxy['name'] = proxy['name'].replace(" ", "")
    # 清除emoji
    proxy['name']=re.sub('["\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"]', '', proxy['name'])
    
    # 处理字符串替换
    for ele in repl_names:
        _ori_str = ele['ori']
        _repl_str = ele['repl']
        # proxy['name'] = proxy['name'].replace(_ori_str, _repl_str)
        proxy['name'] = re.sub(_ori_str,_repl_str, proxy['name'] )

    # 替换mirror
    if proxy['server'] in server_mirr_dict.keys():
        proxy['server'] = server_mirr_dict.get(proxy['server'], proxy['server'])
    
    # 节点名字加上前缀
    proxy['name'] = name_prefix_str + proxy['name'].replace(" ", "")
    
    return proxy


def get_client_agent(client_typ=ClientApp.browser):

    agents_dict={
            ClientApp.shadowrocket:"Shadowrocket/1907 CFNetwork/1406.0.4 Darwin/22.4.0",
            ClientApp.clash:"clash-verge/v1.3.0",
            ClientApp.browser:"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.54"
        }

    default_agent = agents_dict[ClientApp.browser]
    
    return agents_dict.get(client_typ, default_agent)


class ProxyProtocol():
    shadowsocks = "shadowsocks"
    http = "http"
    shadowtls= "shadowtls"
    trojan = "trojan"
    hysteria = "hysteria"
    vmess = "vmess"
    naive = "naive"
    vmess = "vmess"
    vless = "vless"
    tproxy = "tproxy"


class ServiceState():
    inactive = "inactive"
    active = "active"
    failed = "faild"
    unknown = "unknown"
    notfound = "notfound"


def get_sub_info(sub_str_head):
    _eles = [ele for ele in sub_str_head.split("; ")]
    _eles2 = [ele.split("=") for ele in _eles]
    sub_info = { ele[0]: int(ele[1]) for ele in _eles2 }
    return sub_info

def xj_update_dict(base:dict, update:dict):
    # 仅支持两级更新
    for k,v in update.items():
        if k in base.keys():
            b_v = base[k]
            if isinstance(b_v, dict) and isinstance(v, dict):
                b_v.update(v)
            else:
                b_v = v
            base[k] = b_v
        else:
            base[k] = v

def load_server_profile(service):
    env = configs.env
    
    if service == 'xray':
        server_profile_file=env['xray_profile']
    else:
        server_profile_file=env['singbox_profile']
    
    server_profile = yaml.load(open(server_profile_file, 'r'))
    users = configs.users
    
    server_profile['users'] = users
    
    return server_profile


def load_server_config(config_json_path):
    return json.load(open(config_json_path, 'r'))


def load_subscribe_tp(server_profile, tp_type=ClientApp.clashmeta):

    if tp_type == ClientApp.singbox:
        subscribe_tp = yaml.load(open(server_profile['subscribe_singbox_tp'], 'r'))
    elif tp_type == ClientApp.clashmeta:
        subscribe_tp = yaml.load(open(server_profile['subscribe_clashmeta_tp'], 'r'))
    elif tp_type == ClientApp.clash:
        subscribe_tp = yaml.load(open(server_profile['subscribe_clash_tp'], 'r'))
    else:
        raise Exception("未知的订阅模板类型")

    return subscribe_tp


def dump_server_config(server_cfg, dst_server_cfg):
    dir_path = os.path.dirname(dst_server_cfg)
    os.makedirs(dir_path,exist_ok=True)
    
    json.dump(server_cfg, open(dst_server_cfg, 'w+'), sort_keys=False, indent=2, separators=(',', ':'))
    # yaml.dump(subscribe_tp, open(args.dst_server_cfg,'w+'))


def get_service_state(service='sing-box'):
    # return active, failed, inactive
    cmd = f"systemctl status {service}"
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    out = p.communicate()[0].decode('utf8')
    if "Active: inactive" in out:
        return ServiceState.inactive
    if "Active: active" in out:
        return ServiceState.active
    if "FAILURE" in out:
        return ServiceState.failed
    if "not be found" in out:
         ServiceState.notfound
    
    return ServiceState.unknown

def get_random_password():
    return b64encode(token_bytes(16)).decode()

def service_op(op="status", service='sing-box'):
    # 操作服务状态，并返回操作完成后的结果
    cmd = f"systemctl {op} {service}"
    print(cmd)
    p = subprocess.Popen(cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    
    # return get_service_state()


def get_default_resp_data():
    # 返回值模版
    return {"code": 1, "info": "ok"}


def base64_encode(string):
    """
    Removes any `=` used as padding from the encoded string.
    """
    encoded = base64.urlsafe_b64encode(string).decode()
    return encoded.rstrip("=")

def base64_decode(string):
    """
    Adds back in the required padding before decoding.
    """
    padding = 4 - (len(string) % 4)
    string = string + ("=" * padding)
    return base64.urlsafe_b64decode(string)

def get_public_key_from_private_x25519(private_key_string):
    
    private_key = base64_decode(private_key_string)
    public_key = x25519.scalar_base_mult(private_key)

    return base64_encode(public_key)
    
def b64en(str_content):
    return base64.b64encode(str_content.encode()).decode()

def urlen(str_content):
    safe_string = urllib.parse.quote_plus(str_content)
    return safe_string
