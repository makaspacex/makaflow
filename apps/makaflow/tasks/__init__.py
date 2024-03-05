
from .update_subscribe_task import UpdateSubThread
from .update_repo_task import UpdateRepoThread
from .update_repo_task import UpdateQureRepoThread
from ..third.substore_server import ProxyConverServer
from apps.makaflow.models import Repo
from .load_file_init import load_all
from apps.makaflow import configs

def start_update_repo_task():
    global _threadings
    repos = Repo.objects.all()
    for repo in repos:
        _thre = UpdateRepoThread(repo)
        _thre.start()
        configs._threadings[repo.id] = _thre

def start_sub_task():
    UpdateSubThread().start()

def start_all_tasks():
    start_update_repo_task()
    start_sub_task()
    
    # UpdateQureRepoThread().start()
    # ProxyConverServer().start()
    
    