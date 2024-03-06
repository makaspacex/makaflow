
from collections.abc import Callable, Iterable, Mapping
import threading
import time
from typing import Any
from apps.makaflow import configs
import os
import subprocess
import sys
import glob
from pathlib import Path
import json

class BaseTask(threading.Thread):
    def __init__(self, name=None) -> None:
        threading.Thread.__init__(self)
        self._kill = threading.Event()
        self.task_name = f"{self.__class__.__name__}"
        if name:
            self.task_name = name
        self.info(f"已创建")
    
    def info(self, str_content):
        self.display(str_content=str_content, tag="INFO")
    
    def error(self, str_content):
        self.display(str_content=str_content, tag="ERROR")
    
    def display(self, str_content, tag='INFO'):
        print(f"{tag} {self.task_name} {str_content}")
    
    def kill(self):
        self._kill.set()
    
    def sleep(self,seconds) -> bool:
        is_killed = self._kill.wait(seconds)
        if is_killed:
            return True
        return False
        
        
    

