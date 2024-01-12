"""
URL configuration for Makaflow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.apps import apps
from pathlib import Path
import importlib

from . import get_local_installed_app_names

urlpatterns = [
    path('admin/', admin.site.urls),
]

# 将本地app的url加入到项目中
_installed_apps = get_local_installed_app_names()
for _app_name in _installed_apps:
    _app_name_path = _app_name.replace('.', '/')
    app_path = Path(_app_name_path) / "apps.py"
    if not app_path.exists():
        continue
    m_path = f'{_app_name}.urls'
    module = importlib.import_module(m_path)
    if hasattr(module, "urlpatterns"):
        urlpatterns += getattr(module, "urlpatterns")

