"""MediaAI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.apps import apps as dj_apps
from django.urls import path
from apps.makaflow import  api

namespace = 'api'
app_name = 'makaflow'
# slaver
urlpatterns = [
    path('serverop/<op>', api.slaver.api_service_op),
    path('serverlog/<service>>', api.slaver.api_server_log),
    path('serverconfig/<service>', api.slaver.api_server_config),
    path('serverstate', api.slaver.api_user_state),
    path('update_config', api.slaver.api_update_config),
]
from django.urls import re_path
urlpatterns += [
    path('subscrib', api.manager.api_subscrib),
    path('generate_config/<service>', api.manager.api_generate_config),
    path('push_config', api.manager.api_push_config),
    path('push_service_op/<op>', api.manager.api_push_service_op),
    path('get_service_status', api.manager.api_get_service_status),
    path('loadall', api.manager.api_loadall),
    path('rule/geo/<client>/<code>.<suffix>', api.manager.api_rule),
    path('conf/<conf>', api.manager.api_conf),
    re_path(r'icon/(?P<path>.*)', api.manager.api_icon),
    re_path(r'rule/bm7/(?P<path>.*)', api.manager.api_rule_bm7),
]

def init():
    from django.conf import settings
    from django.urls import include
    from apps.makaflow import urls as maka_urls
    urls = __import__(settings.ROOT_URLCONF).urls
    urls.urlpatterns.append(
        path(r'{}/'.format(maka_urls.namespace), include('apps.makaflow.urls', namespace=maka_urls.namespace))
    )

if dj_apps.is_installed('apps.admin'):
    home_need_auth = []
    home_noneed_auth = []
