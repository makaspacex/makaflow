from base64 import b64encode
from secrets import token_bytes
from copy import deepcopy
import numpy as np
from apps.makaflow import tools
from .common import ClientApp
from apps.makaflow.tools.common import ProxyProtocol
from apps.makaflow.tools.common import human_traffic
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
import os
import json
import ruamel

from apps.makaflow.tools.subscrib_common import get_inbound_index
from apps.makaflow.tools.subscrib_common import get_inbound_by_tag
from apps.makaflow.tools.subscrib_common import get_shadowtls_password
from apps.makaflow.tools.subscrib_common import conv_yaml_obj_to_json
from apps.makaflow.tools.subscrib_common import get_user_by_uname
from apps.makaflow.tools.subscrib_common import get_updated_sharelink
from apps.makaflow.tools.subscrib_common import get_ports
from apps.makaflow.tools.subscrib_common import conve_v2
from apps.makaflow.tools.common import b64en, urlen
from apps.makaflow import tools
from apps.makaflow.convert.converter import convertsV2Ray
from apps.makaflow.tools.convert_api import xj_convert
from apps.makaflow.tools.common import proxy_process

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
        
        ports = get_ports(inbound['port'])
        port_infos = [ {"port":port, "server_url":server_url} for port in ports ]
        
        portfp = inbound.get('portfp', None)
        if portfp:
            port_infos = portfp
        
        
        for pt_i in port_infos:
            _inbound = copy.deepcopy(inbound)
            _inbound['port'] = pt_i['port']
            _inbound['server_url'] = pt_i['server_url']
            all_inbounds.append(_inbound)
    
    return all_inbounds

# 从xray生成配置文件
def get_outbonds_for_xray(inbounds, client_type, user, nodename, node_conf, share_link=False):
    
    outbounds_result = []

    # 重新生成inbounds，因为有转发和多端口的情况存在
    server_url = node_conf['server_url']
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
    proxy_tps = env['proxy_tps_from_xray']
    

    for inbound in inbounds_new:
        p_type = inbound['protocol']
        client = None
        
        # 一般情况下都是这样的存贮路径
        clients = inbound.get('settings', {}).get('clients', [])
        for cc in clients:
            # 判email是否相等
            if cc['email'] == user['email']:
                client = cc
                break
        
        # 找到符合条件的配置模板
        out_tp:dict = None
        for _tp in proxy_tps:
            meta = _tp['meta']
            protocol = _tp['protocol']
            
            if protocol != p_type:
                continue
            
            if client_type not in meta['app']:
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
            "inbound":inbound,
            "client":client,
            "slaver":slaver,
            "pub":get_public_key_from_private_x25519,
            "b64en":b64en,
            "urlen":urlen
            }
        
        # out_bound = {}
        # for key, value in out_tp.items():
        #     conve_v(out_bound, key, value, env_vars)
        
        if share_link:
            sss = out_tp.get("share_link", None)
            if sss:
                out_bound = conve_v2(sss, env_vars)
                outbounds_result += [out_bound]
        else:
            out_bound = conve_v2(out_tp['content'], env_vars)
            outbounds_result += [out_bound]
    
    return outbounds_result


# TODO 从singbox生成配置文件
def get_outbonds_for_singbox(inbounds, client_type, user, nodename, node_conf, share_link=False):
    
    outbounds_result = []

    # 重新生成inbounds，因为有转发和多端口的情况存在
    server_url = node_conf['server_url']
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
    proxy_tps = env['proxy_tps_from_singbox']
    

    for inbound in inbounds_new:
        p_type = inbound['protocol']
        client = None
        
        # 一般情况下都是这样的存贮路径
        clients = inbound.get('settings', {}).get('clients', [])
        for cc in clients:
            # 判email是否相等
            if cc['email'] == user['email']:
                client = cc
                break
        
        # 找到符合条件的配置模板
        out_tp:dict = None
        for _tp in proxy_tps:
            meta = _tp['meta']
            protocol = _tp['protocol']
            
            if protocol != p_type:
                continue
            
            if client_type not in meta['app']:
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
            "inbound":inbound,
            "client":client,
            "slaver":slaver,
            "pub":get_public_key_from_private_x25519,
            "b64en":b64en,
            "urlen":urlen
            }
        
        # out_bound = {}
        # for key, value in out_tp.items():
        #     conve_v(out_bound, key, value, env_vars)
        
        if share_link:
            sss = out_tp.get("share_link", None)
            if sss:
                out_bound = conve_v2(sss, env_vars)
                outbounds_result += [out_bound]
        else:
            out_bound = conve_v2(out_tp['content'], env_vars)
            outbounds_result += [out_bound]
    
    return outbounds_result

def render_tp(user:dict, client_type=ClientApp.clash):
    
    env = configs.env
    third_subs_profile = configs.third_subs_profile
    
    share_link = False
    if client_type in ClientApp.sharelink_group:
        share_link = True

    nodes = env['slaver']['nodes']
    config_dir = env['server_config_dir']
    
    # 用于存贮最终的结果
    outbounds_result = []
    # 1、找出第三方订阅的节点服务
    res_info = {"upload":0, "download":0, "total":0, "expire":0}
    third_subs = env['third_sub']
    for nodename, node_conf in third_subs.items():
        
        sub_enable = node_conf['sub_enable']
        if not sub_enable:
            continue
        
        server_config = None
        
        # yaml数据订阅
        server_config = third_subs_profile.get(nodename, None)
        if server_config is None:
            continue
        
        # 处理订阅信息头
        sub_header_str = server_config.get('subscription_userinfo', None)
        subinfo = None
        if sub_header_str:
            subinfo = tools.get_sub_info(server_config['subscription_userinfo'])
            # 查看是否过期
            now_secs = int(time.time())
            if now_secs > subinfo['expire']:
                continue
            # 查看流量是否用超了
            if subinfo['upload'] + subinfo['download'] > subinfo['total']:
                continue
            
            # 更新到订阅结果里面
            res_info['upload'] += subinfo['upload']
            res_info['download'] += subinfo['download']
            res_info['total'] += subinfo['total']
            res_info['expire'] = max(subinfo['expire'], res_info['expire'])
        
        # ---------------------------- 开始处理订阅的节点信息 ---------------------------
        proxies = server_config['proxies']
        suffix = ""
        if subinfo:
            # remain_rate =  1 - ((subinfo['upload'] + subinfo['download'] ) / subinfo['total'])
            # suffix = f"|{int(remain_rate*100)}"
            expire = datetime.fromtimestamp(subinfo['expire'])
            diff = expire - datetime.now()
            
            _remain = subinfo['total'] - subinfo['download'] - subinfo['upload']
            h_str = human_traffic(_remain)
            suffix = f"|{diff.days}D|{h_str}"
            
        
        for proxy in proxies:
            # 处理节点的名字，mirr名称和过滤节点
            proxy = proxy_process(node_name=nodename, node_conf=node_conf, proxy=proxy, suffix=suffix)
            if proxy is None:
                continue
            outbounds_result += [conv_yaml_obj_to_json(proxy)]
        
        # if client_type in ClientApp.clash_group or client_type in ClientApp.clashmeta_group:
        #     proxies = server_config['proxies']
        #     for proxy in proxies:
        #         res = proxy_process(node_name=nodename, node_conf=node_conf, proxy=proxy)
        #         if res is None:
        #             continue
        #         outbounds_result += [conv_yaml_obj_to_json(proxy)]
        
        # elif client_type in ClientApp.sharelink_group:
        #     if not os.path.exists(config_path_sharelink):
        #         continue
        #     with open(config_path_sharelink, 'r') as f:
        #         lines = f.read().splitlines()
        #     for line in lines:
        #         try:
        #             proxy = xj_convert(line, 'JSON')
        #             res = proxy_process(node_name=nodename, node_conf=node_conf, proxy=proxy)
        #             if res is None:
        #                 continue
        #             line = xj_convert(proxy, 'URI')
        #         except Exception as e:
        #             print(line)
        #             print(e)
        #         outbounds_result += [line]

    # 2、找出singbox的节点服务
    for nodename, node_conf in nodes.items():
        enable = node_conf['sub_enable']
        if not enable:
            continue
        
        server_url = node_conf['server_url']
        prefix = node_conf['prefix']    
        singbox_config_path = os.path.join(config_dir, f"{nodename}_singbox.json")
        if not os.path.exists(singbox_config_path):
            continue
        
        server_config = json.load(open(singbox_config_path,'r'))
        inbounds = server_config['inbounds']
        outbounds = get_outbonds_for_singbox(inbounds, client_type, user, nodename, node_conf, share_link=share_link)
        
        outbounds_result += outbounds
        
    # 3、找出xray的节点服务
    for nodename, node_conf in nodes.items():
        
        enable = node_conf['sub_enable']
        if not enable:
            continue

        xray_config_path = os.path.join(config_dir, f"{nodename}_xray.json")
        if not os.path.exists(xray_config_path):
            continue
        
        server_config = json.load(open(xray_config_path,'r'))
        inbounds = server_config['inbounds']
        outbounds = get_outbonds_for_xray(inbounds, client_type, user, nodename, node_conf, share_link=share_link)
        
        outbounds_result += outbounds
    
    
    resp_text, resp_headers = "error", {}
    resp_headers['subscription-userinfo'] = "; ".join([ f"{k}={v}" for k,v in res_info.items()])
    
    
    # 模板是clash系列的话
    if client_type in (ClientApp.clashmeta_group + ClientApp.clash_group ):
        
        if client_type == ClientApp.stash:
            config_tp = copy.deepcopy(configs.sub_tps['stash_tp'])
        elif client_type == ClientApp.clashmeta:
            config_tp = copy.deepcopy(configs.sub_tps['clashmeta_tp'])
        elif client_type == ClientApp.clash:
            config_tp = copy.deepcopy(configs.sub_tps['clash_tp'])
        else:
            raise Exception(f"未知的客户端类型{client_type}")
        # QX: QX_Producer(),
        # Surge: Surge_Producer(),
        # SurgeMac: SurgeMac_Producer(),
        # Loon: Loon_Producer(),
        # Clash: Clash_Producer(),
        # ClashMeta: ClashMeta_Producer(),
        # URI: URI_Producer(),
        # V2Ray: V2Ray_Producer(),
        # JSON: JSON_Producer(),
        # Stash: Stash_Producer(),
        # ShadowRocket: ShadowRocket_Producer(),
        
        
        # 最终的出口结果，模板中的也要继承
        if not isinstance(config_tp['proxies'], list):
            config_tp['proxies'] = []
        config_tp['proxies'] =  config_tp['proxies'] + outbounds_result
        all_outbound_tags = []
        for proxy in config_tp['proxies']:
            all_outbound_tags += [proxy['name']]
        
        _new_groups = []
        for i, proxy_g in enumerate(config_tp["proxy-groups"]):
            if not isinstance(proxy_g['proxies'], list):
                proxy_g['proxies'] = []
            # 转化为基本的list，输出标准格式的yaml
            proxy_g['proxies'] = list(proxy_g['proxies'])
            
            filter_re = proxy_g.get("filter", '.*')
            out_tags = []
            for proxy_name in all_outbound_tags:
                if not re.search(filter_re, proxy_name, re.I):
                    continue
                out_tags += [proxy_name]
            proxy_g['proxies'] += out_tags
            
            # 代理组下无节点就跳过
            if len(proxy_g['proxies']) == 0:
                continue
            
            _new_groups += [proxy_g]
        
        config_tp["proxy-groups"] = _new_groups
        
        out_ = StringIO()
        yaml = ruamel.yaml.YAML()
        yaml.indent(sequence=4, offset=2)
        yaml.dump(config_tp,out_)
        out_.seek(0)
        resp_text = out_.read()
    
    elif client_type in ClientApp.sharelink_group:
        target = "URI"
        if client_type in ClientApp.sub_store_support:
            target = client_type
        outbounds_result = xj_convert(outbounds_result, target)
        
        resp_text = str(outbounds_result)
        
        resp_text = base64.b64encode(resp_text.encode()).decode()
    elif client_type == ClientApp.surge:
        target = "sruge"
        if client_type in ClientApp.sub_store_support:
            target = client_type
        names = [x['name'] for x in outbounds_result]
        outbounds_result = xj_convert(outbounds_result, target)
        surge_tp:str = configs.sub_tps['surge_tp']
        proxys = str(outbounds_result)
        
        # 替换托管token
        surge_tp = surge_tp.replace('token=123456',f'token={user["token"]}')
        
        # 替换代理列表
        surge_tp = surge_tp.replace("#{PROXYLIST}#", proxys)
        
        # 替换策略组列表
        re_p = re.compile(r'#\{filter: *"(.*?)"\}#',re.I)
        while True:
            re_obj = re.search(re_p, surge_tp)
            if re_obj is None:
                break
            _filter_re  = re_obj.group(1)
            _out_tags = ""
            for proxy_name in names:
                if not re.search(_filter_re, proxy_name, re.I):
                    continue
                _out_tags += f"{proxy_name},"
            
            if len(_out_tags) > 0:
                surge_tp = surge_tp.replace(re_obj.group(0),_out_tags[:-1])
        resp_text = surge_tp
        
    return resp_text, resp_headers