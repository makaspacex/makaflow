# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models

# from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.html import format_html

from common.models import BaseModel
from common.util.storage import UUIDFileName
from apps.makaflow import configs

class Subscribe(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField('名称', max_length=256,blank=True)
    sub_enable = models.BooleanField("可订阅", default=True)
    prefix = models.CharField('前缀', max_length=256,blank=True, default="")
    use_proxy = models.BooleanField('通过代理', default=False)
    sub_url = models.CharField('订阅地址', max_length=512,blank=True, default="")
    subscription_userinfo = models.CharField('订阅信息', max_length=512,blank=True,default="")
    autoupdate = models.BooleanField('自动更新',default=True)
    interval = models.IntegerField('更新间隔',default=7200)

    repl_names = models.CharField('名称替换', max_length=256,blank=True)
    node_includes = models.CharField('节点包含', max_length=512,blank=True,default="")
    node_excludes = models.CharField('节点排除', max_length=512,blank=True,default="")
    server_mirr = models.CharField('镜像地址替换', max_length=256,blank=True,default="")
    content = models.TextField('订阅内容',blank=True,default="")
    sub_groups = models.CharField("订阅组", max_length=512 , blank=True,default="")
    order = models.IntegerField("排序",default=1)
    
    def up_thred_status(self):
        _th = configs._sub_thrd.get(self.id,None)
        if _th and _th.is_alive():
            return True
        return False
    up_thred_status.short_description = '更新线程状态'
    
    class Meta:
        verbose_name = '订阅'
        verbose_name_plural = '订阅管理'
    
    def __str__(self):
        return self.name

class Repo(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField('名称', max_length=256)
    url = models.CharField('仓库地址', max_length=256)
    path = models.CharField('本地路径', max_length=256)
    interval = models.IntegerField('更新间隔',default=7200)
    autoupdate = models.BooleanField('自动更新',default=True)
    version = models.CharField('当前版本', max_length=256, blank=True,null=True)
    
    def up_thred_status(self):
        _th = configs._repo_thrds.get(self.id,None)
        if _th and _th.is_alive():
            return True
        return False
    up_thred_status.short_description = '更新线程状态'
    
    class Meta:
        verbose_name = '仓库'
        verbose_name_plural = '仓库管理'
    
    def __str__(self):
        return self.name
  