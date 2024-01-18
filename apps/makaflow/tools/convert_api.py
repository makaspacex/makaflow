import requests
import json
import yaml


def xj_convert(data, target):
    p_data = data
    if isinstance(data, dict):
        p_data = json.dumps(data)
    elif isinstance(data, list):
        ele = data[0]
        if isinstance(ele, dict):
            p_data=yaml.dump({"proxies": data})
        elif isinstance(ele, str):
            p_data = "\n".join(data)
    elif isinstance(data, str):
        if '\n' in  data:
            raise Exception("一个字符串包含多行时, 请使用list")
    
    api_url = "http://localhost:3000/api/proxy/parse"
    req_data = {
        "data":p_data,
        "client": target
    }
    
    resp = requests.post(api_url, json=req_data)
    res = resp.json()
    
    ret = res['data']['par_res']
    if (not isinstance(data, list)) and isinstance(ret, list):
        ret = ret[0]
    
    return ret

    
if __name__ == "__main__":
    
    demo_a = '{"name":"Lv3 香港 01 [2.0]","type":"ss","server":"v3-hk.kunlun-sd.com","port":"6601","cipher":"aes-128-gcm","password":"e17e96b3-88a9-42c6-87c7-20e89854ac2f"}'
    
    demo_b = 'ss://YWVzLTEyOC1nY206ZTE3ZTk2YjMtODhhOS00MmM2LTg3YzctMjBlODk4NTRhYzJm@v3-hk.kunlun-sd.com:6601#Lv3%20%E9%A6%99%E6%B8%AF%2001%20%5B2.0%5D'
    
    demo_c = {"name":"Lv3 香港 01 [2.0]","type":"ss","server":"v3-hk.kunlun-sd.com","port":"6601","cipher":"aes-128-gcm","password":"e17e96b3-88a9-42c6-87c7-20e89854ac2f"}
    
    demo_d = [demo_c, demo_c, demo_c]
    demo_e = [demo_b, demo_b, demo_b]
    
    import time
    s = time.time()
    for i in range(2):
        # xj_convert(demo_a, "URI")
        print(xj_convert(demo_b, "JSON"))
        print(xj_convert(demo_c, "URI"))
        # xj_convert(demo_c, "Loon")
        print(xj_convert(demo_d, "Loon"))
        print(xj_convert(demo_e, "JSON"))
    
    cost = time.time() -s
    print( cost/10)
    
    
    
    
    
    
    
    
    
    
    
    


