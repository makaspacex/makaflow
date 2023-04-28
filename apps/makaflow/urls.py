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
from django.conf.urls import url

from apps.makaflow import controler, api

home_need_auth = [
    url(r'^$', controler.views.index_page),
    url(r'^page/index/$', controler.views.index_page),
    url(r'^page/index$', controler.views.index_page),
]

if dj_apps.is_installed('apps.admin'):
    home_need_auth = []
    home_noneed_auth = []
