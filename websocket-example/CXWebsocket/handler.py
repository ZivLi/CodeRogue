from threading import Thread
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor


class BaseHandler:
    def __init__(self, name, topic: (str, list) = None, *args, **kwargs):
        self.name = name
        self.topic = set(topic if isinstance(topic, list) else
                        [topic]) if topic is not None else set()
        self._thread_pool = ThreadPoolExecutor(max_workers=1)
        self.__active = False

    def run(self):
        pass