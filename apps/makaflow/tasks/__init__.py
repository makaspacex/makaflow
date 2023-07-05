
from .update_subscribe_task import UpdateSubThread
from .update_rule_repo_task import UpdateBm7RepoThread
from .update_rule_repo_task import UpdateQureRepoThread
from . load_file_init import load_all



def start_tasks():
    UpdateSubThread().start()
    UpdateBm7RepoThread().start()
    UpdateQureRepoThread().start()
    
    