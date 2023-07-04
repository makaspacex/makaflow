from .geo_type import common_pb2
from .geo_type import common
import importlib
import re 
import ruamel.yaml
from io import StringIO
import os
from apps.makaflow import configs



def load_geosites(f_path) -> dict[str, list[common.Domain]]:
    with open(f_path, 'rb') as f:
        gsite_list = common_pb2.GeoSiteList()
        _ = gsite_list.ParseFromString(f.read())
    gsite_list:list[common.GeoSite] = sorted(list(gsite_list.entry), key=lambda x: x.country_code)
    gsite_list = { x.country_code.lower():x.domain for x in gsite_list}
    
    return gsite_list

def load_geoips(f_path) -> dict[str, list[str]]:
    with open(f_path, 'rb') as f:
        gip_list = common_pb2.GeoIPList()
        _ = gip_list.ParseFromString(f.read())
    gip_list = sorted(list(gip_list.entry), key=lambda x: x.country_code)
    res = {}
    for geo_ip in gip_list:
        cs = []
        for cidr in geo_ip.cidr:
            hex_str = cidr.ip.hex()
            _l, _d = 2, '.'
            if len(hex_str) == 32:
                _l, _d = 4, ':'
            _rr = re.findall(r'.{'+ f"{_l}" +r'}',hex_str) 
            if  _l == 2:
                _rr = [ str(int(x, 16)) for x in _rr ]
            ip_str  = _d.join(_rr)
            cs.append(f"{ip_str}/{cidr.prefix}")
            
        res[geo_ip.country_code.lower()] = cs
    return res


def get_domains_by_country_code(country_code:str, geosites:dict[str, list[common.Domain]]) -> list[common.Domain]:
    
    if country_code in geosites:
        return geosites[country_code]
    if '@' not in country_code:
        raise Exception(f'not supported country_cde:{country_code}')
    real_code, rule = country_code.split('@')
    
    if real_code not in geosites:
        return []

    domains = geosites[real_code]
    
    contain_mode = True
    if '!' in rule:
        contain_mode = False
    d_n = rule.split('!')[-1]
    
    res = []
    for doamin in domains:
        if contain_mode:
            if doamin.value.endswith(f".{d_n}") or doamin.value.startswith(f"{d_n}."):
                res.append(doamin)
        else:
            if doamin.value.endswith(f".{d_n}") or doamin.value.startswith(f"{d_n}."):
                pass
            else:
                res.append(doamin)
    return res


def clash_rules(geosites:dict[str, list[common.Domain]], geoips:dict[str, list[str]], country_code:str):
    country_code = country_code.lower()
    cidrs = geoips.get(country_code, [])
    domains = get_domains_by_country_code(country_code=country_code, geosites=geosites)
    
    content = ""
    content += f"# NAME: {country_code}\n"
    content += f"# AUTHOR: makaflow\n"
    content += f"# TOTAL: {len(domains)+ len(cidrs)}\n"
    
    hosts = []
    for domain in domains:
        if  domain.type == 2:
            hosts.append(f"DOMAIN-SUFFIX,{domain.value}")
        elif  domain.type == 3:
            hosts.append(f"DOMAIN,{domain.value}")
    
    for cidr in cidrs:
        if ":" in cidr:
            hosts.append(f"IP-CIDR6,{cidr}")
        else:
            hosts.append(f"IP-CIDR,{cidr}")
    
    yaml = ruamel.yaml.YAML()
    yaml.indent(sequence=4, offset=2)
    str_io = StringIO()
    yaml.dump({"payload":hosts}, str_io)
    str_io.seek(0)
    content += str_io.read()
    
    # write to file for debug
    g_tmp_dir = configs.env['g_tmp_dir']
    out_dir = os.path.join(g_tmp_dir, "clash")
    os.makedirs(out_dir, exist_ok=True)
    dest_f = os.path.join(out_dir, f"{country_code}.yaml")
    f = open(dest_f, "w+")
    f.write(content)
    f.close()

    return content


def loon_rules(geosites:dict[str, list[common.Domain]], geoips:dict[str, list[str]], country_code:str):
    country_code = country_code.lower()
    cidrs = geoips.get(country_code, [])
    domains = get_domains_by_country_code(country_code=country_code, geosites=geosites)
    
    content = ""
    content += f"# NAME: {country_code}\n"
    content += f"# AUTHOR: makaflow\n"
    content += f"# TOTAL: {len(domains)+ len(cidrs)}\n"
    
    hosts = []
    for domain in domains:
        if  domain.type == 2:
            hosts.append(f"DOMAIN-SUFFIX,{domain.value}")
        elif  domain.type == 3:
            hosts.append(f"DOMAIN,{domain.value}")
    
    for cidr in cidrs:
        if ":" in cidr:
            hosts.append(f"IP-CIDR6,{cidr}")
        else:
            hosts.append(f"IP-CIDR,{cidr}")
    
    content += "\n".join(hosts)
    
    # write to file for debug
    g_tmp_dir = configs.env['g_tmp_dir']
    out_dir = os.path.join(g_tmp_dir, "loon")
    os.makedirs(out_dir, exist_ok=True)
    dest_f = os.path.join(out_dir, f"{country_code}.list")
    f = open(dest_f, "w+")
    f.write(content)
    f.close()

    return content

# def loon_rules(geosite_list, geoip_list, dest_dir):
#     pass

# # icloud@cn 包含在了 apple@cn
# # apple@cn 和 apple-cn不是一回事

# dest_dir = "rules"
# country_codes = ['category-games@cn','steam','google-cn', 'apple@cn','apple-cn','microsoft@cn','geolocation-cn']
# clash_rules(geosites, geoips, "rules/", country_codes=country_codes)

