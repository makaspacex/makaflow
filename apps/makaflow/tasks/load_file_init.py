import ruamel.yaml
yaml = ruamel.yaml.YAML()
import os
import glob
from apps.makaflow import configs
from apps.makaflow.tools.geo import load_geoips, load_geosites

def load_env(env_path="env.yaml"):
    print(f"loading env form {env_path}")
    env_config = yaml.load(open(env_path, 'r'))
    configs.env = env_config
    return env_config

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
    # 加载订阅模板文件
    load_sub_tps()
    # 加载geo文件
    load_geo()
    
    


    

