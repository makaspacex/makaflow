from copy import deepcopy
from apps.makaflow.tools import common
import numpy as np
from apps.makaflow import configs
import os
import requests
import json

def generate_inbounds(interface_item, rand_num, server_profile):

    tag, interface = interface_item
    users = server_profile['users']
    
    inbounds_res = []
    
    # 当前监听服务的描述信息
    meta = interface["meta"]
    p_content = interface["content"]
        
    tag_suffix = p_content['listen_port'] if "listen_port" in p_content.keys() else f"{rand_num:04d}"
    new_tag = f"{tag}-{tag_suffix}"
    
    shadowtls_cfg = server_profile['inbounds']['shadowtls']
    listen_common = server_profile['inbounds']['listen']
    tls_common = server_profile['inbounds']['tls']
    trans_common = server_profile['inbounds']['transport']

    shadowtls_tp = shadowtls_cfg['common']
    shadowtls_tp.update(listen_common)
    v2_tp = shadowtls_cfg['v2']
    
    # 生成shadowtls来通信
    if meta['shadowtls_mode'] in ['all', 'only_tls']:
        
        s_p = meta['tls_s_port']
        
        # 为保证兼容性 生成三个版本的配置
        # v1-v3的tls配置
        v1_shadow_tls = deepcopy(shadowtls_tp)
        listen_port = s_p
        v1_shadow_tls.update(
            {"tag":f"shadowtls-{listen_port}","listen_port": listen_port, "version": 1, "detour": new_tag})
        inbounds_res += [v1_shadow_tls]
        
        v2_shadow_tls = deepcopy(shadowtls_tp)
        listen_port += 1
        v2_shadow_tls.update(
            {"tag":f"shadowtls-{listen_port}","listen_port": listen_port, "version": 2, "detour": new_tag})
        v2_shadow_tls.update(v2_tp)
        inbounds_res += [v2_shadow_tls]
        

        v3_shadow_tls = deepcopy(shadowtls_tp)
        listen_port += 1
        users_dt = [ {"name":x['name'],'password':x['password']} for x in users]
        v3_shadow_tls.update(
            {"tag":f"shadowtls-{listen_port}","listen_port": listen_port, "version": 3, "detour": new_tag, "users": users_dt})

        inbounds_res += [v3_shadow_tls]
    
    # 构建监听入口
    res_content = {"tag": new_tag}
    common.xj_update_dict(res_content, listen_common)
    
    if meta['use_tls']:
        res_content['tls'] = tls_common
    if meta['use_transport']:  
        res_content['transport'] = trans_common
    common.xj_update_dict(res_content, interface['content'])
    if meta['shadowtls_mode'] == 'only_tls':
        # 如果仅通过tls服务，则禁用外网监听
        res_content['listen'] = "127.0.0.1"
    
    # 是否支持多用户
    if meta['support_multiuser']:
        users_res = []
        for user in users:
            _u = {}
            for tkey, ukey in meta.get("user_field_map").items():
                _u[tkey] = user.get(ukey,ukey)
            users_res.append(_u)
        res_content.update({"users": users_res})
    else:
        # TODO 不支持多用户的情况下处理
        pass
    
    inbounds_res += [res_content]
    
    return inbounds_res
    

def update_singbox(server_profile, node_info):

    # 读取userconfig，更新到运行目录并重启服务器，然后查看服务器状态
    server_cfg_res = {}

    # dns 相关
    server_cfg_res['dns'] = server_profile['dns']

    # log 相关
    server_cfg_res['log'] = server_profile['log']
    
    server_cfg_res['outbounds'] = server_profile['outbounds']
    server_cfg_res['route'] = server_profile['route']
    
    random_numbers = np.arange(2000)
    np.random.shuffle(random_numbers)
    random_numbers = list(random_numbers)
    
    # 生成配置文件的inbounds
    inbounds_res = []
    interfaces = server_profile['inbounds']['interfaces']
    for tag, interface in interfaces.items():
        meta = interface["meta"]
        content = interface["content"]
        num,step,tls_s_port,listen_port = meta['num'],meta['step'], meta['tls_s_port'],content['listen_port']
        
        for _i in range(num):
            # 修改interface的meta字段和content字段
            interface['meta']['tls_s_port'] = tls_s_port + _i * step
            interface['content']['listen_port'] = listen_port + _i * step
                            
            rand_num = random_numbers[0]
            del random_numbers[0]
            
            interface_item = tag, interface
            res_content_list = generate_inbounds(interface_item, rand_num, server_profile)
            inbounds_res += res_content_list
    
    server_cfg_res['inbounds'] = inbounds_res
    
    common.dump_server_config(server_cfg_res, server_profile["dst_server_cfg"])


def update_xray(server_profile, node_info):
    env = configs.env
    node_name, node_conf = node_info
    
    if not node_conf['enable']:
        return
    # 读取userconfig，更新到运行目录并重启服务器，然后查看服务器状态
    server_cfg_res = {}

    # dns 相关
    server_cfg_res['dns'] = server_profile['dns']
    server_cfg_res['api'] = server_profile['api']
    server_cfg_res['stats'] = server_profile['stats']

    # log 相关
    server_cfg_res['log'] = server_profile['log']
    
    server_cfg_res['outbounds'] = server_profile['outbounds']
    server_cfg_res['routing'] = server_profile['routing']
    
    random_numbers = np.arange(2000)
    np.random.shuffle(random_numbers)
    random_numbers = list(random_numbers)
    
    # 生成配置文件的inbounds
    inbounds_res = []
    
    # 直接配置的
    inbounds_res += server_profile['inbounds']['come-inbound']
    
    users = server_profile['users']
    
    interfaces = server_profile['inbounds']['interfaces']
    for tag, interface in interfaces.items():
        meta = interface["meta"]
        if not meta['enable']:
            continue
        
        mode = meta.get("mode", 'all')
        
        
        res_content = {}
        res_content['tag'] = tag
        content = interface["content"]
        common.xj_update_dict(res_content, content)
        
        # 处理转发订阅的信息
        portfp = res_content.get('portfp', None)
        if portfp:
            res_content.pop("portfp")
        
        _p = None
        if portfp:
            for server_name, p_info in portfp.items():
                if server_name != node_name:
                    continue
                _p = p_info
                break
        
        if mode in ['only_pf']:
            if not _p:
                continue
            else:
                res_content['portfp'] = p_info
        elif mode in ['only_me']:
            res_content.pop("portfp")
        
        elif mode in ['all']:
            if _p:
                res_content['portfp'] = p_info
        
        # 是否支持多用户
        if meta['support_multiuser']:
            users_res = []
            for user in users:
                _u = {}
                for tkey, ukey in meta.get("user_field_map").items():
                    _u[tkey] = user.get(ukey,ukey)
                users_res.append(_u)
            res_content['settings']['clients'] = users_res
        
        inbounds_res.append(res_content)
    
    server_cfg_res['inbounds'] = inbounds_res
    
    
    dst_server_cfg = os.path.join(env['server_config_dir'], f"{node_name}_xray.json")
    common.dump_server_config(server_cfg_res, dst_server_cfg)
    
    # 建议手动push到节点
    # push到远程节点node
    
    # 重启远程节点node
    # 建议手动调用API重启
    
    
def update(service):
    nodes = configs.env['slaver']['nodes']
    
    server_profile=common.load_server_profile(service)
    for node_info in nodes.items():
        if service == 'singbox':
            update_singbox(server_profile=server_profile,node_info= node_info)
        elif service == 'xray':
            update_xray(server_profile=server_profile,node_info= node_info)

    
def push_config():
    nodes = configs.env['slaver']['nodes']
    env = configs.env
    server_config_dir = env['server_config_dir']
    res_data = {}
    
    for node_name, node_conf in nodes.items():
        try:
            api_base = node_conf['api_base']
            rpc_key = node_conf['rpc_key']
            enabled = node_conf['enable']
            if not enabled:
                continue
            
            data = {"xray_config":"{}", "singbox_config":"{}"}
            
            xray_config_path = os.path.join(server_config_dir, f"{node_name}_xray.json")
            if os.path.exists(xray_config_path):
                xray_config = open(f"{xray_config_path}",'r').read()
                data['xray_config'] = xray_config

            singbox_config_path = os.path.join(server_config_dir, f"{node_name}_singbox.json")
            if os.path.exists(singbox_config_path):
                singbox_config = open(f"{singbox_config_path}",'r').read()
                data['singbox_config'] = singbox_config
            
            push_api_url = f"{api_base}/update_config"
            
            resp = requests.post(push_api_url,data=data, headers={"rpckey":rpc_key})
            if resp.status_code != 200:
                raise Exception(resp.reason)
            
            resp_json = resp.json()
            resp_json['api_base'] = api_base
            res_data[f"{node_name}"] = resp_json
        except Exception as e:
            res_data[f"{node_name}"] = f"failed: {e}"
        
    return res_data

    
def test_xray():
    service = 'xray'
    server_profile = common.load_server_profile(service)
    update_xray(server_profile)
    

if __name__ == "__main__":
    test_xray()