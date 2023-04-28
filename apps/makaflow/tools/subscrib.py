from base64 import b64encode
from secrets import token_bytes
from copy import deepcopy
import numpy as np
import tools
from tools.common import ClientApp
from tools.common import ProxyProtocol


def get_inbound_index(inbounds, tag):
    for i, inbound in enumerate(inbounds):
        if 'tag' in inbound.keys() and tag == inbound['tag']:
            return i
    return -1            

def get_inbound_by_tag(inbounds, tag):
    
    for i, inbound in enumerate(inbounds):
        if 'tag' in inbound.keys() and tag == inbound['tag']:
            return inbound
    return None

def get_shadowtls_password(inbound_stls, username):
     # shadowtls的password
    tls_password = None
    if inbound_stls['version'] == 2:
        tls_password = inbound_stls["password"]
    elif inbound_stls['version'] == 3:
        password = [x['password'] for x in inbound_stls['users'] if x['name'] == username][0]
        tls_password = password
    return tls_password


# 可以处理singbox, clash, stash, clasmeta, shadowrocket类型的订阅
def process_inbounds(server_url, protocol_defult, inbound, username, detour_bound=None, prefix="", suffix="", client=ClientApp.singbox):
    
    _ppp = None
    p_type = inbound['type']
    detour_key = detour_bound['tag'] if detour_bound is not None else None
    
    # 处理shadowsocks类型的信息
    if p_type == ProxyProtocol.shadowsocks:
        _upass = [x['password'] for x in inbound['users'] if x['name'] == username][0]
        password = f"{inbound['password']}:{_upass}"
        _ccc_out_name = f"{prefix}{p_type}{suffix}{'-'+ str(inbound.get('listen_port',''))}"
        
        _ppp = {}
        if client == ClientApp.singbox:
            _ppp['multiplex'] = protocol_defult['multiplex']
            tools.xj_update_dict(_ppp,protocol_defult.get("shadowsocks", {}))
            tools.xj_update_dict(_ppp, {
                "type": "shadowsocks",
                "tag": _ccc_out_name,
                "method": inbound['method'],
                "password": password,
            })
            
        # 处理clashmeta，和小火箭
        elif client in [ClientApp.clashmeta,ClientApp.shadowrocket]:
            tools.xj_update_dict(_ppp,protocol_defult.get("ss", {}))
            tools.xj_update_dict(_ppp, { "type": "ss",
                    "cipher": inbound['method'],
                    "name": _ccc_out_name,
                    "password": password,
                    "port": inbound['listen_port'],
                    "server": server_url
                })
            
    elif p_type == ProxyProtocol.http:
        password = [ x['password'] for x in inbound['users'] if x['username'] == username][0]
        _ccc_out_name = f"{prefix}{p_type}{suffix}{'-'+ str(inbound.get('listen_port',''))}"
        _ppp = {}
        if client == ClientApp.singbox:
            tools.xj_update_dict(_ppp,protocol_defult.get("http", {}))
            tools.xj_update_dict(_ppp, {
            "type": "http",
            "tag": _ccc_out_name,
            "username": username,
            "password": password,
            })
            
        # 处理clashmeta，和小火箭
        elif client in [ClientApp.clashmeta,ClientApp.shadowrocket]:
            tools.xj_update_dict(_ppp,protocol_defult.get("http", {}))
            tools.xj_update_dict(_ppp, {
                    "type": "http",
                    "name": _ccc_out_name,
                    "username": username,
                    "password": password,
                    "server": server_url,
                    "port": inbound['listen_port'],
                    })
            
    
    elif p_type == ProxyProtocol.trojan:
        _ccc_out_name = f"{prefix}{p_type}{suffix}{'-'+ str(inbound.get('listen_port',''))}"
        password = [ x['password'] for x in inbound['users'] if x['name'] == username][0]
        
        _ppp = {}
        if client == 'singbox':
            _ppp['multiplex'] = protocol_defult['multiplex']
            tools.xj_update_dict(_ppp,protocol_defult.get("trojan", {}))
            tools.xj_update_dict(_ppp, {
            "tag": _ccc_out_name,
            "password":password,
            "type": "trojan",
            "network": "tcp",
            "tls":{
                "disable_sni": False,
                "insecure": False,
                "alpn": inbound['tls']['alpn'],
                "min_version": inbound['tls']['min_version'],
                "max_version": inbound['tls']['max_version'],
                "cipher_suites": inbound['tls']['cipher_suites']
            },
            "transport":inbound['transport']
            })
            

        # 处理clashmeta，和小火箭
        elif client in ['clashmeta','shadowrocket']:
            tools.xj_update_dict(_ppp,protocol_defult.get("trojan", {}))
            tools.xj_update_dict(_ppp,  {
                "name": _ccc_out_name,
                "server": server_url,
                "port": inbound['listen_port'],
                "password":password,
                "type": "trojan",
                "network": "ws",
                "sni": server_url,
                "udp": True,
                "ws-opts":{
                    "path": inbound['transport']['path']
                }
            })
    elif p_type == ProxyProtocol.hysteria:
        _ccc_out_name = f"{prefix}{p_type}{suffix}{'-'+ str(inbound.get('listen_port',''))}"
        password = [ x['auth_str'] for x in inbound['users'] if x['name'] == username][0]
        
        _ppp = {}
        if client == 'singbox':
            pass
        # 处理clashmeta，和小火箭
        elif client in ['clashmeta','shadowrocket']:
            tools.xj_update_dict(_ppp, protocol_defult.get("hysteria", {}))
            tools.xj_update_dict(_ppp,  {
                "name": _ccc_out_name,
                "type": "hysteria",
                "server": server_url,
                "auth_str": password,
                "password": password, # shadowrocket兼容
                "obfsParam": inbound['obfs'], # shadowrocket兼容
                "port": inbound['listen_port'],
                "obfs":inbound['obfs'],
                "protocol": "udp",
                "up": inbound['up'],
                "down": inbound['down'],
                "sni": server_url,
                "alpn":inbound['tls']['alpn']
            })
    elif p_type == ProxyProtocol.vless:
        _ccc_out_name = f"{prefix}{p_type}{suffix}{'-'+ str(inbound.get('listen_port',''))}"
        password = [ x['uuid'] for x in inbound['users'] if x['name'] == username][0]
        _ppp = {}
        if client == 'singbox':
            pass
        # 处理clashmeta，和小火箭
        elif client in ['clashmeta','shadowrocket']:
            tools.xj_update_dict(_ppp, protocol_defult.get("vless", {}))
            
            tools.xj_update_dict(_ppp,  {
                "name": _ccc_out_name,
                "type": "vless",
                "server": server_url,
                "port": inbound['listen_port'],
                "uuid": password,
                "network": 'tcp',
                "tls": True,
                "udp": True,
                "flow": "xtls-rprx-vision",
                "udp": True,
                "servername": inbound['tls']['reality']['handshake']['server'],
                "reality-opts":{
                    "short-id": "123445",
                    "public-key": "9miEQ4yRqLkR_rS0f2kDukzyR_Z_-GUKpnbORvzMjAE"
                },
                "client-fingerprint": "chrome"
            })
    # 处理shadowtls
    if client in [ClientApp.clashmeta, ClientApp.shadowrocket]:
        if detour_key is not None:
            tls_password = get_shadowtls_password(detour_bound, username)
            _ppp['name'] = f"{prefix}{p_type}{suffix}{'-'+ str(detour_bound.get('listen_port',''))}"
            _ppp.update({
                "server": server_url,
                "port": detour_bound['listen_port'],
                "plugin": "shadow-tls",
                "plugin-opts": {
                    "host": detour_bound['handshake']["server"],
                    "version" : str(detour_bound['version']),
                    "password": tls_password
                }
            })
            if client == ClientApp.shadowrocket:
                _ppp.pop("plugin-opts")
                
                _ppp['pluginParam'] = {
                    "version" : str(detour_bound['version']),
                    "host" : detour_bound['handshake']["server"]
                }
                if detour_bound['version'] in [2,3]:
                     _ppp['pluginParam']['password'] = tls_password
                
                
    elif client == ClientApp.singbox:
        if detour_key is None:
            _ppp.update({
                "server": server_url,
                "server_port": inbound['listen_port']
            })
        else:
            _ppp['detour'] = detour_key
            _ppp['tag'] = f"{prefix}{p_type}{suffix}{'-'+ str(detour_bound.get('server_port',''))}"
    
    return _ppp
    

# 已废弃
def vless(inbound, client_type, user, server_url, prefix) -> list:
    
    res_out = []
    out_tag_names = []
    
    env = configs.env
    username = user['name']
    
    inbound_type = 'xray' if "protocol" in inbound.keys() else "singbox"
    
    portfp = False
    
    if inbound_type == 'xray':
        p_type = inbound['protocol']
        uuid = [ x['id'] for x in inbound['settings']['clients'] if x['id'] == user['uuid_str']][0]
        flow = [ x['flow'] for x in inbound['settings']['clients'] if x['id'] == user['uuid_str']][0]
        ports = get_ports(inbound['port'])
        
        portfp = inbound.get('portfp', None)
        if portfp:
            ports = portfp
        
        private_key_string, servername, short_id = "", "", ""
        network = inbound['streamSettings']['network']
        
        security = inbound['streamSettings']['security']
        if security == 'reality':
            private_key_string = inbound['streamSettings']['realitySettings']['privateKey']
            servername = inbound['streamSettings']['realitySettings']['serverNames'][0]
            short_ids = inbound['streamSettings']['realitySettings']['shortIds']
            short_id = [x for x in short_ids if x != ""][0]
        
        if network == 'ws':
            ws_path = inbound['streamSettings']['wsSettings']['path']
        
    elif inbound_type == 'singbox':
        p_type = inbound['type']
        uuid = [ x['uuid'] for x in inbound['users'] if x['name'] == username][0]
        flow = [ x['flow'] for x in inbound['users'] if x['name'] == username][0]
        ports = inbound['listen_port']
        private_key_string, servername, short_id = "", "", ""
        
        # TODO 
        network = 'tcp'
        
        
        security = "reality" if inbound['tls']['reality']['enabled'] else "tls"
        
        if security == 'reality':
            private_key_string = inbound['tls']['reality']['private_key']
            servername = inbound['tls']['reality']['handshake']['server']
            short_ids = inbound['tls']['reality']['short_id']
            short_id = [x for x in short_ids if x != ""][0]
        
    else:
        raise Exception('unknown server type')
    
    
    if client_type in [ClientApp.clashmeta,ClientApp.shadowrocket]:
        # 过滤小火箭，暂时不支持
        if client_type == ClientApp.shadowrocket:
            return [], []
        
        protocol_defult = env.get('clashmeta_proxies_default', {})
        
        for port_info in ports:
            port = port_info
            if portfp:
                port = port_info['port']
                server_url = port_info['server_url']
            _ppp = {}
            _ccc_out_name = f"{prefix}|{p_type}|{port}"
            tools.xj_update_dict(_ppp, protocol_defult.get("vless", {}))
            tools.xj_update_dict(_ppp,  {
                "name": _ccc_out_name,
                "type": "vless",
                "server": server_url,
                "port": port,
                "uuid": uuid,
                "network": network,
                "tls": True,
                "udp": True,
                "flow": flow,
                "udp": True,
                "client-fingerprint": "chrome"
            })
            if network in ['ws']:
                _ppp['ws-opts'] = {"path": ws_path}
            
            if  security == 'reality':
                
                public_key = get_public_key_from_private_x25519(private_key_string=private_key_string)
                _ppp['servername'] = servername
                _ppp['reality-opts'] = {
                    "short-id": short_id,
                    "public-key": public_key
                }
            elif security == 'tls':
                _ppp['skip-cert-verify'] = False
                if client_type == ClientApp.shadowrocket:
                    _ppp['xtls'] = 2
            
            out_tag_names.append(_ccc_out_name)
            res_out.append(_ppp)
            
    return out_tag_names, res_out

# 已废弃
def shadowsocks(inbound, client_type, user, server_url, prefix) -> list:
    
    res_out = []
    out_tag_names = []
    
    env = configs.env
    username = user['name']
    
    inbound_type = 'xray' if "protocol" in inbound.keys() else "singbox"
    portfp = False
    
    if inbound_type == 'xray':
        p_type = inbound['protocol']
        ports = get_ports(inbound['port'])
        portfp = inbound.get('portfp', None)
        
        if portfp:
            ports = portfp
            
        network = inbound['network']
        cipher = inbound['settings']['method']
        password1 = inbound['settings']['password']
        password = [ x['password'] for x in inbound['settings']['clients'] if x['name'] == user['name']][0]
        password=f"{password1}:{password}"
        udp_true = False
        if 'udp' in network:
            udp_true = True
        
        
    elif inbound_type == 'singbox':
       pass
    else:
        raise Exception('unknown server type')
    
    # 客户端类型
    if client_type in [ClientApp.clashmeta, ClientApp.shadowrocket]:
        
        protocol_defult = env.get('clashmeta_proxies_default', {})
        for port_info in ports:
            port = port_info
            if portfp:
                port = port_info['port']
                server_url = port_info['server_url']
            _ppp = {}
            _ccc_out_name = f"{prefix}|{p_type}|{port}"
            tools.xj_update_dict(_ppp, protocol_defult.get("shadowsocks", {}))
            tools.xj_update_dict(_ppp,  {
                "name": _ccc_out_name,
                "type": "ss",
                "server": server_url,
                "port": port,
                "cipher": cipher,
                "password": password,
                "udp": udp_true,
            })
            
            out_tag_names.append(_ccc_out_name)
            res_out.append(_ppp)
            
    return out_tag_names, res_out
# 已废弃
def _get_outbonds(inbounds, client_type, user, server_url, prefix):
    # 开始处理协议
    outbounds_result = []
    all_outbound_tags = []
    for inbound in inbounds:
        p_type = inbound['protocol']
        out_bound = None
        
        if p_type == ProxyProtocol.vless:
            out_tag_names, out_bound = vless(inbound, client_type, user, server_url, prefix)
        
        if p_type == ProxyProtocol.shadowsocks:
            out_tag_names, out_bound = shadowsocks(inbound, client_type, user, server_url, prefix)
        
        if out_bound != None:
            outbounds_result += out_bound
            all_outbound_tags += out_tag_names

    return outbounds_result, all_outbound_tags

def process_tls_out_for_singbox(inbound_stls, server_url, username):
    _tls_info = { 
        "type": "shadowtls",  
        "tag": inbound_stls['tag'],
        "version":inbound_stls["version"],
        "server": server_url,
        "server_port": inbound_stls['listen_port'],
        "tls": { "enabled": True, "server_name": inbound_stls['handshake']["server"] } 
        }
    if inbound_stls['version'] in [2,3]:
        password = get_shadowtls_password(inbound_stls, username)
        _tls_info['password'] = password
    
    return _tls_info

def singbox(server_profile, server_config,  config_tp, username, client_type="singbox"):

    country_code = server_profile['contry']

    server_url = server_profile['server_url']

    client_shadowtls_versions = server_profile['client_shadowtls_versions'].get(client_type, [])
    
    
    # 最终的出口结果，模板中的也要继承
    outbounds_result = config_tp['outbounds']
    
    all_outbound_tags = []


    random_numbers = np.arange(2000)
    np.random.shuffle(random_numbers)
    random_numbers = list(random_numbers)

    
    protocol_defult = server_profile['singbox_outbound_default']
    processed_tags = []

    # 开始处理协议    
    inbounds = server_config['inbounds']
    for inbound in inbounds:
        p_type = inbound['type']

        # 看是否已经被处理过
        tag = inbound.get("tag", None)
        if tag in processed_tags:
            if tag is not None:
                processed_tags.append(tag)
            continue
        
        out_bound = None
        
        if p_type == ProxyProtocol.shadowtls:
            # 这种类型的inbound不是真正的inbound 会有其他协议辅助才行，所以不会是直连
            # 版本过滤
            s_version = inbound["version"]
            if s_version not in client_shadowtls_versions:
                continue
            
            # 先加入stls的信息
            _tls_info = process_tls_out_for_singbox(inbound, server_url, username=username)
            outbounds_result += [ _tls_info]
            
            # 一定含有detour标签, 标记这个出站的detour为当前
            detour_tag = inbound['detour']
            
            d_bound = get_inbound_by_tag(inbounds=inbounds, tag=detour_tag)
            if "127.0.0.1" in d_bound['listen']:
                processed_tags.append(detour_tag) # 标记为已经处理
            out_bound = process_inbounds(server_url, protocol_defult, d_bound, username, prefix=f"{country_code}-", suffix=f"-v{s_version}", detour_bound=_tls_info, client=client_type)
            
        else:
            if 'tag' in inbound.keys():
                processed_tags.append(inbound['tag'])
            out_bound = process_inbounds(server_url, protocol_defult, inbound, username, detour_bound=None, prefix=f"{country_code}-", client=client_type)

        outbounds_result += [out_bound]
        all_outbound_tags.append(out_bound['tag'])

    
    # 生成final出站 selector tag为final, 默认为直连
    final_outbound =  {
            "type": "selector",
            "tag": "final",
            "outbounds": all_outbound_tags + ['direct'],
            "default": 'direct'
            }
    
    outbounds_result.append(final_outbound)
    # 整合完成，替换原本的配置
    config_tp["outbounds"] = outbounds_result
    
    return config_tp


def clashmeta(server_profile, server_config,  config_tp, username, client_type=ClientApp.clash):

    country_code = server_profile['contry']
    server_url = server_profile['server_url']

    client_shadowtls_versions = server_profile['client_shadowtls_versions'].get(client_type, [])
    

    # 最终的出口结果，模板中的也要继承
    outbounds_result = config_tp['proxies']
    
    all_outbound_tags = []


    random_numbers = np.arange(2000)
    np.random.shuffle(random_numbers)
    random_numbers = list(random_numbers)

    
    protocol_defult = server_profile['clashmeta_proxies_default']
    processed_tags = []

    # 开始处理协议    
    inbounds = server_config['inbounds']
    for inbound in inbounds:
        p_type = inbound['type']

        # 看是否已经被处理过
        tag = inbound.get("tag", None)
        if tag in processed_tags:
            if tag is not None:
                processed_tags.append(tag)
            continue
        
        out_bound = None
        
        if p_type == "shadowtls":
            # 这种类型的inbound不是真正的inbound 会有其他协议辅助才行，所以不会是直连
            # 版本过滤
            s_version = inbound["version"]
            if s_version not in client_shadowtls_versions:
                continue
            
            # 一定含有detour标签, 标记这个出站的detour为当前
            detour_tag = inbound['detour']
            d_bound = get_inbound_by_tag(inbounds=inbounds, tag=detour_tag)
            if "127.0.0.1" in d_bound['listen']:
                processed_tags.append(detour_tag) # 标记为已经处理
            out_bound = process_inbounds(server_url, protocol_defult, d_bound, username, prefix=f"{country_code}-", suffix=f"-v{s_version}", detour_bound=inbound, client=client_type)
            
        else:
            if 'tag' in inbound.keys():
                processed_tags.append(inbound['tag'])
            out_bound = process_inbounds(server_url, protocol_defult, inbound, username, detour_bound=None, prefix=f"{country_code}-", client=client_type)

        outbounds_result += [out_bound]
        all_outbound_tags.append(out_bound['name'])
    
    config_tp['proxies'] = outbounds_result
    
    for i, proxy_g in enumerate(config_tp["proxy-groups"]):
        if not isinstance(proxy_g['proxies'], list):
            proxy_g['proxies'] = []
        proxy_g['proxies'] += all_outbound_tags
        config_tp["proxy-groups"][i] = proxy_g
    
    # config_tp["proxy-groups"][0]['proxies'] = all_outbound_tags
    
    return config_tp

# def clashmeta_bak(server_profile, server_config,  config_tp, username,client_shadowtls_versions=[2], is_shadowrocket = False):

#     contry_code = server_profile['contry']
#     server_url = server_profile['server_url']

#     # 最终的出口结果，模板中的也要继承
#     proxy_result = config_tp['proxies']
#     all_proxy_names = []

#     # 依靠tag来索引信息比较方便
#     inbound_info = {}
#     for inbound in server_config['inbounds']:
#         tag = inbound.get("tag", False)
#         if not tag:
#             continue
#         inbound['processed'] = False
#         inbound_info[tag] = inbound

#     random_numbers = np.arange(2000)
#     np.random.shuffle(random_numbers)
#     random_numbers = list(random_numbers)

#     protocol_defult = server_profile['outbounds']['protocol_defult']
    
#     for inbound in server_config['inbounds']:
#         p_type = inbound['type']

#         # 看是否已经被处理过
#         tag = inbound.get("tag", False)
#         if tag and inbound_info[tag]['processed']:
#             continue
        
#         if p_type == "shadowtls":
#             # 这种类型的inbound不是真正的inbound 会有其他协议辅助才行，所以不会是直连
#             shadowtls_in = inbound

#             # 一定含有detour标签
#             detour_tag = shadowtls_in['detour']
#             detour_bound = inbound_info[detour_tag]
#             inbound_info[detour_tag]['processed'] = True
#             s_version = shadowtls_in["version"]
#             if s_version not in client_shadowtls_versions:
#                 continue
            
#             # ================================
                
#             _ccc_out_tag = None
            
            
            
#             # 处理shadowsocks类型的信息
#             if detour_bound['type'] == "shadowsocks":
#                 _upass = [x['password'] for x in detour_bound['users'] if x['name'] == username][0]
#                 _ccc_out_tag = f"{contry_code}-ss-v{s_version}"
                
#                 _ppp = { "type": "ss",
#                     "cipher": detour_bound['method'],
#                     "name": _ccc_out_tag,
#                     "password": f"{detour_bound['password']}:{_upass}",
#                     "port": shadowtls_in['listen_port'],
#                     "server": server_url,
#                     "udp": True,
#                     "plugin": "shadow-tls",
#                     "plugin-opts": {
#                         "host": shadowtls_in['handshake']["server"],
#                         "password": tls_password
#                         }
#                 }
                
#                 if is_shadowrocket:
#                     _ppp.pop("plugin-opts")
#                     _ppp['pluginParam'] = {
#                         "version" : s_version,
#                         "host" : shadowtls_in['handshake']["server"]
#                     }
                
#                 proxy_result.append(_ppp)
                
#             elif detour_bound['type'] == "http":
#                 password = [ x['password'] for x in detour_bound['users'] if x['username'] == username][0]
#                 _ccc_out_tag = f"{contry_code}-http-v{s_version}"
#                 _ppp = {}
                
#                 proxy_result.append(_ppp)
            
#             # 处理完成
#             if _ccc_out_tag is not  None:
#                 all_proxy_names.append(_ccc_out_tag)
#         elif p_type == "trojan":
#             _ccc_out_tag = f"{contry_code}-tron-ws"
#             password = [ x['password'] for x in inbound['users'] if x['name'] == username][0]
#             _ppp =
            
#             proxy_result.append(_ppp)
#             # 处理完成
#             all_proxy_names.append(_ccc_out_tag)
    
    
    
#     return config_tp
    
        