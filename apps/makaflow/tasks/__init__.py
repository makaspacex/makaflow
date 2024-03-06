
from .update_subscribe_task import UpdateSubscribeThread
from .update_repo_task import UpdateRepoThread
from apps.makaflow.models import Repo
from apps.makaflow.models import Subscribe
from apps.makaflow import configs
from .load_file_init import load_all

def start_update_repo_task():
    repos = Repo.objects.all()
    for repo in repos:
        _thre = UpdateRepoThread(repo)
        _thre.start()
        configs._repo_thrds[repo.id] = _thre

def start_sub_task():
    subs = Subscribe.objects.all()
    for sub in subs:
        _thre = UpdateSubscribeThread(sub)
        _thre.start()
        configs._sub_thrd[sub.id] = _thre

def start_all_tasks():
    start_update_repo_task()
    start_sub_task()
    
    # UpdateQureRepoThread().start()
    # ProxyConverServer().start()
    
    