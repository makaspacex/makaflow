
import os
import glob

import ruamel.yaml
yaml = ruamel.yaml.YAML()

class AppMode:
    manager = "manager"
    node = "node"

# env file
env=None
def load_env(env_path="env.yaml"):
    global env
    print(f"loading env form {env_path}")
    env_config = yaml.load(open(env_path, 'r'))
    env = env_config
load_env()

# 加载用户表
users = []
def load_users():
    global users
    user_profile_path = env['user_profile_path']
    print(f"loading users form {user_profile_path}")
    users = yaml.load(open(user_profile_path, 'r'))
    users = users['users']
load_users()

# 第三方订阅文件，因为很慢，所以需要提前加载到内存
third_subs_profile = {}
def load_third_sub_profile():
    global third_subs_profile
    
    config_dir = env['server_config_dir']
    third_subs = env['third_sub']
    for nodename, node_conf in third_subs.items():
        
        sub_enable = node_conf['sub_enable']
        if not sub_enable:
            continue
        config_path = os.path.join(config_dir, f"{nodename}.yaml")
        config_path_sharelink = os.path.join(config_dir, f"{nodename}.txt")
        
        server_config = None
        
        if os.path.exists(config_path):
            # yaml数据订阅
            print(f"loading {nodename} subinfo form  {config_path}")
            server_config = yaml.load(open(config_path,'r'))
            third_subs_profile[nodename] = server_config
        
load_third_sub_profile()

# 加载订阅模板文件
sub_tps = {}
def load_sub_tps():
    global sub_tps
    tps_dir = env['subscribe_tp_dir']
    tp_file_list = glob.glob(os.path.join(tps_dir, "*_tp.yaml"))
    for tp_file_path in tp_file_list:
        name = os.path.basename(tp_file_path).split(".")[0]
        print(f"loading {name} sub tp form  {tp_file_path}")
        sub_tps[name] = yaml.load(open(tp_file_path,'r'))
load_sub_tps()
