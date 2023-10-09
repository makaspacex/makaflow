from base64 import b64encode
from secrets import token_bytes
from copy import deepcopy
import numpy as np
from apps.makaflow import tools
from apps.makaflow.tools.common import ClientApp
from apps.makaflow.tools.common import ProxyProtocol
from apps.makaflow.tools.common import get_public_key_from_private_x25519
from apps.makaflow import configs
from apps.makaflow.tools import common
import requests
from io import StringIO
from datetime import datetime
import time
import os
import re
import copy
import urllib.parse
import base64
from apps.makaflow.tools.common import yaml
import json
from apps.makaflow.tools.common import urlen, b64en
from apps.makaflow.tasks import load_file_init

def get_inbound_index(inbounds, tag):
    for i, inbound in enumerate(inbounds):
        if "tag" in inbound.keys() and tag == inbound["tag"]:
            return i
    return -1


def get_inbound_by_tag(inbounds, tag):
    for i, inbound in enumerate(inbounds):
        if "tag" in inbound.keys() and tag == inbound["tag"]:
            return inbound
    return None


def get_shadowtls_password(inbound_stls, username):
    # shadowtls的password
    tls_password = None
    if inbound_stls["version"] == 2:
        tls_password = inbound_stls["password"]
    elif inbound_stls["version"] == 3:
        password = [
            x["password"] for x in inbound_stls["users"] if x["name"] == username
        ][0]
        tls_password = password
    return tls_password


# 从users中找出指定的user
def get_user_by_uname(users, user_name):
    for user in users:
        if user["name"] == user_name:
            return user

    return None


# 处理 xray的多端口监听
def get_ports(ports_str):
    ports_raw = str(ports_str)
    ports = []
    for pps in ports_raw.split(","):
        _ps = pps.split("-")
        if len(_ps) > 1:
            ports += list(range(int(_ps[0]), int(_ps[1]) + 1))
        else:
            ports += [int(pps)]
    return ports


# 处理xray多端口和转发
def _generate_inbounds_for_xray(inbounds, server_url):
    """处理xray多端口和转发
    Args:
        inbounds (_type_): inbounds对象
        server_url (_type_): node 的 url
    Returns:
        _type_: _description_
    """
    # 增加 server_url
    # 更改端口 port
    all_inbounds = []

    for inbound in inbounds:
        ports = get_ports(inbound["port"])
        port_infos = [{"port": port, "server_url": server_url} for port in ports]

        portfp = inbound.get("portfp", None)
        if portfp:
            port_infos = portfp

        for pt_i in port_infos:
            _inbound = copy.deepcopy(inbound)
            _inbound["port"] = pt_i["port"]
            _inbound["server_url"] = pt_i["server_url"]
            all_inbounds.append(_inbound)

    return all_inbounds


# 将带有代码的python 转换为实际值
def conve_v2(yaml_dict, env_vars):
    if isinstance(yaml_dict, list):
        return list(yaml_dict)

    # 递归出口条件1
    if isinstance(yaml_dict, int) or isinstance(yaml_dict, bool):
        return yaml_dict

    # 递归出口条件2
    if isinstance(yaml_dict, str) and yaml_dict.lower() in ["true", "false"]:
        if yaml_dict.lower() == "true":
            return True
        if yaml_dict.lower() == "false":
            return False

    # 递归出口条件3
    if isinstance(yaml_dict, str):
        if "{" not in yaml_dict:
            return yaml_dict
        else:
            for varname, _vvv in env_vars.items():
                locals()[varname] = _vvv

            _value = yaml_dict.replace("'", '"')
            code = f"f'{_value}'"
            new_v = eval(code)

            if new_v.lower() == "true":
                new_v = True
            elif new_v.lower() == "false":
                new_v = False

            # 尝试转化为int
            try:
                new_v = int(new_v)
            except:
                pass
            return new_v

    if isinstance(yaml_dict, dict):
        red_dict = {}
        for _k, _v in yaml_dict.items():
            red_dict[_k] = conve_v2(_v, env_vars)
        return red_dict
    raise Exception(f"Unkonw type {type(yaml_dict)} {yaml_dict}")


# 替换分享链接中的信息, 含过滤功能
def get_updated_sharelink(line_str, nodename) -> list:
    env = configs.env
    third_subs = env["third_sub"]
    node_conf = third_subs[nodename]

    # 过滤非节点信息
    _r = re.search(r"^\w+://", line_str)
    if not _r:
        return None

    exclude_node = node_conf.get("exclude_node", None)
    name_prefix_str = node_conf.get("prefix", "")
    repl_names = node_conf.get("repl_names", [])
    server_mirr_dict = {
        ele["ori"]: ele["mirr"] for ele in node_conf.get("server_mirr", [])
    }

    # vmess
    if re.search(r"^vmess://(.*)", line_str, re.I):
        # 类型1
        try:
            r = re.search(r"^vmess://(.*)", line_str, re.I)
            content = r.group(1)
            proxy = json.loads(base64.b64decode(content).decode())
            # 处理过滤节点
            if exclude_node:
                _r = re.search(exclude_node, proxy["ps"])
                if _r:
                    return None

            return line_str
        except Exception:
            pass

        # 类型2
        try:
            r = re.search(r"^vmess://(.*?)\?.*?remark=(.*?)&.*", line_str, re.I)
            if not r:
                return None

            server_name = r.group(2)
            if exclude_node:
                _r = re.search(exclude_node, server_name)
                if _r:
                    return None

            return line_str
        except Exception:
            pass

    # 默认原样返回
    return line_str


# 从xray生成配置文件
def get_outbonds_for_xray(
    inbounds, client_type, user, nodename, node_conf, share_link=False
):
    outbounds_result = []

    # 重新生成inbounds，因为有转发和多端口的情况存在
    server_url = node_conf["server_url"]
    inbounds_new = _generate_inbounds_for_xray(inbounds, server_url)

    # 需要准备的运行环境变量
    # 1、inbound对象，包含修改的的 port 和增加的 server_url
    # 2、client对象，对应请求的client，原封不动的来自于配置文件中的某个client
    # 3、slaver对象，原封不对的来自于env中的slaver下的某个对象
    # 4、通过key的名字来索引对象信息
    #
    # 提供的函数包括
    # 1、pub # 由私钥转为公钥

    pub = get_public_key_from_private_x25519
    slaver = node_conf

    env = configs.env
    proxy_tps = env["proxy_tps_from_xray"]

    for inbound in inbounds_new:
        p_type = inbound["protocol"]
        client = None

        # 一般情况下都是这样的存贮路径
        clients = inbound.get("settings", {}).get("clients", [])
        for cc in clients:
            # 判email是否相等
            if cc["email"] == user["email"]:
                client = cc
                break

        # 找到符合条件的配置模板
        out_tp: dict = None
        for _tp in proxy_tps:
            meta = _tp["meta"]
            protocol = _tp["protocol"]

            if protocol != p_type:
                continue

            if client_type not in meta["app"]:
                continue

            res = eval(f"{meta['condition']}")
            if not res:
                continue

            out_tp = _tp
            break

        if not out_tp:
            continue

        # env_vars = inbound, client, slaver, pub, b64en, urlen

        env_vars = {
            "inbound": inbound,
            "client": client,
            "slaver": slaver,
            "pub": get_public_key_from_private_x25519,
            "b64en": b64en,
            "urlen": urlen,
        }

        # out_bound = {}
        # for key, value in out_tp.items():
        #     conve_v(out_bound, key, value, env_vars)

        if share_link:
            sss = out_tp.get("share_link", "")
            out_bound = conve_v2(sss, env_vars)
        else:
            out_bound = conve_v2(out_tp["content"], env_vars)

        outbounds_result += [out_bound]

    return outbounds_result


# 递归的转换yaml的objt dict为标准的dict
def conv_yaml_obj_to_json(yaml_dict):
    # 数组类型
    if isinstance(yaml_dict, list):
        return list(yaml_dict)

    # 其他不是dict的类型
    if not isinstance(yaml_dict, dict):
        return yaml_dict

    result = {}
    for key, value in yaml_dict.items():
        result[key] = conv_yaml_obj_to_json(value)
    return result

import traceback
# 并行的处理订阅信息，加快响应速度
# 每个订阅都有shadowrocket类型的请求和clash类型的请求
# 固定任务 每个小时都应该主动更新订阅信息
def update_subscribe_cache():
    env = configs.env
    config_dir = env["server_config_dir"]
    third_subs = env["third_sub"]
    proxies = env.get("proxies", {})
    file_changed = False

    for nodename, node_conf in third_subs.items():
        sub_enable = node_conf["sub_enable"]
        if not sub_enable:
            continue
        
        # 判断是否是本地文件
        sub_url = node_conf["sub_url"]
        if not sub_url.startswith("http"):
            continue
        
        config_path = os.path.join(config_dir, f"{nodename}.yaml")
        # config_path_sharelink = os.path.join(config_dir, f"{nodename}.txt")

        server_config = None
        need_update = False
        
        if not os.path.exists(config_path):
            need_update = True
        else:
            config_st_time = os.stat(config_path).st_mtime
            config_st_time = datetime.fromtimestamp(config_st_time)
            now_date = datetime.now()
            diff_t = now_date - config_st_time
            td_hours, _ = divmod(diff_t.seconds, 3600)
            if td_hours >= 1:
                need_update = True
        
        try:
            if need_update:
                headers = {"User-Agent": common.get_client_agent(ClientApp.clash)}
                sub_url = node_conf["sub_url"]
                resp = requests.get(sub_url, headers=headers, proxies=proxies)
                if resp.status_code != 200:
                    raise Exception(f"{nodename} 请求失败")
                subscription_userinfo = resp.headers.get("subscription-userinfo", None)
                sio = StringIO()
                sio.write(resp.text)
                sio.seek(0)
                server_config = yaml.load(sio)
                if server_config is not None:
                    server_config["subscription_userinfo"] = subscription_userinfo
                    yaml.dump(server_config, open(config_path, "w+"))

                # # 订阅式的链接
                # headers = {"User-Agent": common.get_client_agent(ClientApp.browser)}
                # resp = requests.get(sub_url, headers=headers, proxies=proxies)
                # if resp.status_code != 200:
                #     raise Exception(f"{nodename} 请求失败")
                
                # with open(config_path_sharelink, "w+") as f:
                #     re_decode = base64.b64decode(resp.text).decode()
                #     f.write(re_decode)
                file_changed = True
        except Exception as e:
            print(nodename, e)
            print(traceback.format_exc())
            continue
        finally:
            _now = datetime.now().timestamp()
            os.utime(config_path, (_now, _now))

    if file_changed:
        load_file_init.load_third_sub_profile()

if __name__ == "__main__":
    update_subscribe_cache()
    print("end")
