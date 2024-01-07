import ruamel.yaml
yaml = ruamel.yaml.YAML()
import os
import glob
from apps.makaflow import configs
from apps.makaflow.tools.geo import load_geoips, load_geosites
import subprocess

def load_env(env_path="env.yaml"):
    print(f"loading env form {env_path}")
    env_config = yaml.load(open(env_path, 'r'))
    configs.env = env_config

def load_users():
    user_profile_path =  configs.env['user_profile_path']
    print(f"loading users form {user_profile_path}")
    users = yaml.load(open(user_profile_path, 'r'))
    configs.users = users['users']

def load_third_sub_profile():
    
    config_dir =  configs.env['server_config_dir']
    os.makedirs(config_dir, exist_ok=True)
    
    third_subs =  configs.env['third_sub']
    for nodename, node_conf in third_subs.items():
        
        sub_enable = node_conf['sub_enable']
        if not sub_enable:
            continue
        
        config_path = os.path.join(config_dir, f"{nodename}.yaml")
        if not node_conf["sub_url"].startswith("http"):
            config_path = node_conf["sub_url"]
        
        server_config = None
        
        if os.path.exists(config_path):
            # yaml数据订阅
            print(f"loading {nodename} form  {config_path}")
            server_config = yaml.load(open(config_path,'r'))
            configs.third_subs_profile[nodename] = server_config
    
def load_sub_tps():
    tps_dir =  configs.env['subscribe_tp_dir']
    tp_file_list = glob.glob(os.path.join(tps_dir, "*_tp.*"))
    clash_c = open(os.path.join(tps_dir, "_clash_common.yaml"),'r').read()
    
    for tp_file_path in tp_file_list:
        name, suffix = os.path.basename(tp_file_path).split(".")
        
        print(f"loading {name} sub tp form  {tp_file_path}")
        from io import StringIO
        buffer = StringIO()
        content = open(tp_file_path,'r').read()
        buffer.write(content)
        
        if name in ["clash_tp", "clashmeta_tp", "stash_tp"]:
            buffer.write(clash_c)
        
        buffer.seek(0)
        if suffix == 'yaml':
            configs.sub_tps[name] = yaml.load(buffer)
        elif suffix == 'conf':
            configs.sub_tps[name] = buffer.read()
        

def load_geo():
    geosite_file =  configs.env['geosite_file']
    geoip_file =  configs.env['geoip_file']
    
    print(f"loading geosites from {geosite_file}")
    configs.geosites = load_geosites(geosite_file)
    print(f"loading geoips from {geoip_file}")
    configs.geoips = load_geoips(geoip_file)

def load_all():
    # 家在env文件
    load_env()
    # 加载用户表
    load_users()
    # 第三方订阅文件，因为很慢，所以需要提前加载到内存
    load_third_sub_profile()
    # 加载订阅模板文件
    load_sub_tps()
    # 加载geo文件
    load_geo()
    
    


    

