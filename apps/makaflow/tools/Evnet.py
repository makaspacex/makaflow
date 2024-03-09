import threading
from threading import Event
from queue import Queue

from threading import Thread

class __Event():
    def __init__(self,name,type='NAME'):
        pass

class EvnetManager(threading.Thread):
    def __init__(self):
        super().__init__()
        # 待处理的事件队列
        self.queue = Queue()

        # 事件对应的处理器，每个事件有多个注册的处理器
        self.handler = {}

        # 事件循环处理线程
        self.__thread = Thread(target=self.__run)

    def __run(self):
        while True:
            try:
                event = self.queue.get(block=True,timeout=1)
                handler = self.handler.get(event['name'])
                if handler:
                    event.get()
                    handler(*args, **kwargs)


            except Exception as e:
                pass
    def trigger_event(self, event, *args, **kwargs):
        pass
        self.queue.put((event, args, kwargs))

    # 注册一个事件以及对应的处理函数
    def register_event(self, event, handler):
        pass





