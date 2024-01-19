import requests
import json
import yaml
from typing import Tuple,Optional,Union
from apps.makaflow.configs import env

def xj_convert(data, target) -> Union[dict, str]:
    # 确保是字符串，每行一个代理信息
    p_data = data
    if isinstance(data, dict):
        p_data = json.dumps(data)
    elif isinstance(data, list):
        p_data = ""
        for ele in data:
            if isinstance(ele, dict):
                p_data += f"{json.dumps(ele)}\n" 
            elif isinstance(ele, str):
                p_data += f"{ele}\n" 
            else:
                raise Exception("未知的类型")
    else:
        p_data = data
    
    api_url = env['convert_api']
    
    req_data = {
        "data":p_data,
        "client": target
    }
    
    resp = requests.post(api_url, json=req_data)
    res = resp.json()
    if res['status'] == "failed":
        raise Exception(res['error']['message'])
    
    ret = res['data']['par_res']
    if target == 'JSON':
        ret = json.loads(ret)

    elif isinstance(ret, list) and len(ret) == 1:
        ret:str = ret[0]
    
    return ret

    
if __name__ == "__main__":
    
    demo_a = '{"name":"Lv3 香港 01 [2.0]","type":"ss","server":"v3-hk.kunlun-sd.com","port":"6601","cipher":"aes-128-gcm","password":"e17e96b3-88a9-42c6-87c7-20e89854ac2f"}'
    
    demo_b = 'ss://YWVzLTEyOC1nY206ZTE3ZTk2YjMtODhhOS00MmM2LTg3YzctMjBlODk4NTRhYzJm@v3-hk.kunlun-sd.com:6601#Lv3%20%E9%A6%99%E6%B8%AF%2001%20%5B2.0%5D'
    
    demo_c = {"name":"Lv3 香港 01 [2.0]","type":"ss","server":"v3-hk.kunlun-sd.com","port":"6601","cipher":"aes-128-gcm","password":"e17e96b3-88a9-42c6-87c7-20e89854ac2f"}
    
    demo_d = [demo_c, demo_c, demo_c]
    demo_e = [demo_b, demo_b, demo_b]
    demo_f = [demo_a, demo_b, demo_c]
    
    import time
    s = time.time()
    for i in range(1):
        print(xj_convert(demo_a, "URI"))
        print(xj_convert(demo_b, "JSON"))
        print(xj_convert(demo_c, "URI"))
        print(xj_convert(demo_d, "Loon"))
        print(xj_convert(demo_e, "JSON"))
        print("\n")
        print(xj_convert(demo_f, "JSON"),"\n")
        print(xj_convert(demo_f, "Loon"),"\n")
        print(xj_convert(demo_f, "Clash"),"\n")
        print(xj_convert(demo_f, "Surge"),"\n")
    
    cost = time.time() -s
    print( cost/10)
    
    
    
    
    
    
    
    
    
    
    
    


