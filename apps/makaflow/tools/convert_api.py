import requests
import json

def xj_convert(data, target):
    if isinstance(data, dict):
        data = json.dumps(data)
    
    api_url = "http://localhost:3000/api/parser"
    req_data = {
        "data":data,
        "client": target
    }
    resp = requests.get(api_url, params=req_data)
    res = resp.json()
    
    ret = res['data']['par_res']
    if target.lower() == 'json':
        ret= json.loads(ret)
        if isinstance(ret, list) and len(ret) == 1:
            ret = ret[0]
    
    return ret
    
if __name__ == "__main__":
    
    demo_a = '{"name":"Lv3 香港 01 [2.0]","type":"ss","server":"v3-hk.kunlun-sd.com","port":"6601","cipher":"aes-128-gcm","password":"e17e96b3-88a9-42c6-87c7-20e89854ac2f"}'
    
    demo_b = 'ss://YWVzLTEyOC1nY206ZTE3ZTk2YjMtODhhOS00MmM2LTg3YzctMjBlODk4NTRhYzJm@v3-hk.kunlun-sd.com:6601#Lv3%20%E9%A6%99%E6%B8%AF%2001%20%5B2.0%5D'
    
    demo_c = {"name":"Lv3 香港 01 [2.0]","type":"ss","server":"v3-hk.kunlun-sd.com","port":"6601","cipher":"aes-128-gcm","password":"e17e96b3-88a9-42c6-87c7-20e89854ac2f"}
    
    import time
    s = time.time()
    for i in range(20):
        xj_convert(demo_a, "URI")
        xj_convert(demo_b, "JSON")
        xj_convert(demo_c, "URI")
        xj_convert(demo_c, "Loon")
    
    cost = time.time() -s
    print( cost/10)
    
    
    
    
    
    
    
    
    
    
    
    


