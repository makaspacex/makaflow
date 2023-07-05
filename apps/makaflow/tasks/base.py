
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
    def __init__(self, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: Iterable[Any] = ..., kwargs: Mapping[str, Any] | None = None, *, daemon: bool | None = None) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.task_name = f"{self.__class__.__name__}"
        self.info("created")
    
    def info(self, str_content):
        self.display(str_content=str_content, tag="INFO")
    
    def error(self, str_content):
        self.display(str_content=str_content, tag="ERROR")
    
    def display(self, str_content, tag='INFO'):
        print(f"{tag} {self.task_name} {str_content}")
        
        
        
        
    

