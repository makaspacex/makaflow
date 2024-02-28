# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models

# from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.html import format_html

from common.models import BaseModel
from common.util.storage import UUIDFileName


class Subscribe(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField('名称', max_length=256,blank=True)
    sub_enable = models.BooleanField("可订阅", default=True)
    prefix = models.CharField('前缀', max_length=256,blank=True)
    use_proxy = models.BooleanField('通过代理', default=True)
    sub_url = models.CharField('订阅地址', max_length=256)
    subscription_userinfo = models.CharField('订阅信息', max_length=512,blank=True)
    
    repl_names = models.JSONField('名称替换',blank=True)
    content = models.TextField('订阅内容',blank=True)
    server_mirr = models.JSONField('镜像地址替换',blank=True)
    
    class Meta:
        verbose_name = '订阅'
        verbose_name_plural = '订阅管理'
    
    sub_groups = models.ManyToManyField("SubGroup", verbose_name="订阅组", blank=True)
    
    def __str__(self):
        return self.name

class SystemConfig(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField('名称', max_length=256)
    rule = models.CharField('正则表达式', max_length=256)
    
    class Meta:
        verbose_name = '规则'
        verbose_name_plural = '规则管理'
    
    def __str__(self):
        return self.name


class SubGroup(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField('名称', max_length=256)
    
    class Meta:
        verbose_name = '订阅组'
        verbose_name_plural = '订阅组管理'
    
    def __str__(self):
        return self.name

