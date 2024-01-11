from django.contrib import admin
from django.urls import path
from django.apps import apps
from pathlib import Path
import importlib

def get_local_installed_app_names():
    return  [x.name for x in list(apps.get_app_configs())]


