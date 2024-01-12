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
    name = models.CharField('名称', max_length=256,blank=True, null=True)
    sub_enable = models.BooleanField("可订阅", default=True)
    prefix = models.CharField('前缀', max_length=256,blank=True, null=True)
    use_proxy = models.BooleanField('通过代理', default=True)
    sub_url = models.CharField('订阅地址', max_length=256)
    
    
    repl_names = models.JSONField('名称替换',blank=True, null=True)
    content = models.TextField('订阅内容',blank=True, null=True)
    server_mirr = models.JSONField('镜像地址替换',blank=True, null=True)
    
    node_excludes = models.ManyToManyField("Rule", blank=True, null=True, verbose_name="排除规则")
    
    class Meta:
        verbose_name = '订阅'
        verbose_name_plural = '订阅管理'
    
    def __str__(self):
        return self.name


class Rule(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField('名称', max_length=256)
    rule = models.CharField('正则表达式', max_length=256)
    
    class Meta:
        verbose_name = '规则'
        verbose_name_plural = '规则管理'
    
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



