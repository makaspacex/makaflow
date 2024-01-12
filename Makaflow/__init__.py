from django.contrib import admin
from django.urls import path
from django.apps import apps
from pathlib import Path
import importlib

def get_local_installed_app_names():
    return  [x.name for x in list(apps.get_app_configs())]


def get_local_app_urls():
    urlpatterns = []
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
    return urlpatterns
