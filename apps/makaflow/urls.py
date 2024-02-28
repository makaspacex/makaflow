"""MediaAI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('api/', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('api/', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('api/blog/', include('blog.urls'))
"""

from django.apps import apps as dj_apps
from django.urls import path
from apps.makaflow import  api
from django.urls import re_path

namespace = 'api'
app_name = 'makaflow'

need_rpckey, public = [], []

# slaver
need_rpckey += [
    path('api/serverop/<op>', api.slaver.api_service_op),
    path('api/serverlog/<service>', api.slaver.api_server_log),
    path('api/serverconfig/<service>', api.slaver.api_server_config),
    path('api/serverstate', api.slaver.api_user_state),
    path('api/update_config', api.slaver.api_update_config),
]

# manager
need_rpckey += [
    path('api/generate_config/<service>', api.manager.api_generate_config),
    path('api/push_config', api.manager.api_push_config),
    path('api/push_service_op/<op>', api.manager.api_push_service_op),
    path('api/get_service_status', api.manager.api_get_service_status),
]

public += [
    path('api/subscrib', api.manager.api_subscrib_old),
    path('api/v1/client/subscribe', api.manager.api_subscrib_v1),
    path('api/loadall', api.manager.api_loadall),
    path('api/rule/geo/<client>/<code>.<suffix>', api.manager.api_rule),
    re_path(r'api/mixrule/(?P<path>.*)', api.manager.api_mixrule),
    path('api/conf/<conf>', api.manager.api_conf),
    re_path(r'api/resource/(?P<path>.*)', api.manager.api_resource_down),
    re_path(r'api/icon/(?P<path>.*)', api.manager.api_icon),
    re_path(r'api/rule/bm7/(?P<path>.*)', api.manager.api_rule_bm7),
]

urlpatterns = need_rpckey + public

if dj_apps.is_installed('apps.admin'):
    home_need_auth = []
    home_noneed_auth = []
