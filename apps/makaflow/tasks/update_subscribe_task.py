from  apps.makaflow.tools.subscrib_common import update_subscribe_cache
import time
from .base import BaseTask
from apps.makaflow.models import Subscribe
from apps.makaflow.tools.common import ClientApp
from apps.makaflow.tools import common
import requests
from common.models import Config
from io import StringIO
from apps.makaflow.tools.common import yaml
from datetime import datetime,timezone
import json


class UpdateSubscribeThread(BaseTask):
    def __init__(self, sub:Subscribe):
        super().__init__(name=sub.name)
        self.sub = sub
    
    def update(self):
        
        headers = {"User-Agent": common.get_client_agent(ClientApp.clash)}
        conf = Config.objects.filter(key="proxies").first()
        proxies = None
        if conf:
            proxies = json.loads(conf.value)
        
        p_tip = f"正在使用代理{proxies}"
        if not self.sub.use_proxy:
            proxies = None
            p_tip = f"正在不使用代理"
        sub_url = self.sub.sub_url
        self.info(f"{p_tip}请求{sub_url}")
        resp = requests.get(sub_url, headers=headers, proxies=proxies,timeout=6)
        if resp.status_code != 200:
            raise Exception(f"请求失败")
        server_config = yaml.load(resp.text)
        self.info("请求成功")
        
        if server_config is None:
            raise Exception(f"无内容")
        
        res_server_config = {}
        res_server_config['proxies'] = server_config.get("proxies",[])
        
        out_ = StringIO()
        yaml.indent(sequence=4, offset=2)
        yaml.dump(res_server_config,out_)
        out_.seek(0)
        resp_text = out_.read()
        
        self.sub.subscription_userinfo = resp.headers.get("subscription-userinfo", "")
        self.sub.content = resp_text
        
        self.sub.save()
        self.info("已更新")      

    def check(self):
        try:
            self.sub = Subscribe.objects.get(id=self.sub.id)
        except Exception as e:
            return False
        
        if not self.sub.autoupdate:
            return False
        
        sub_url = self.sub.sub_url
        if not sub_url or not sub_url.startswith("http"):
            return False
        
        if (not self.sub.content) or len(self.sub.content)<10:
            return True
        
        last_update = self.sub.updated_at
        now = datetime.now(last_update.tzinfo)
        diff_seconds = (now - last_update).total_seconds()
        if diff_seconds<self.sub.interval:
            return False
        
        return True
    
    def run(self):
        self.info("已启动")
        while not self._kill.is_set():
            try:
                if not self.check():
                    continue
                self.update()
                
            except Exception as e:
                self.error(e)
            finally:
                self.sleep(1)
        
        self.info("已停止")
