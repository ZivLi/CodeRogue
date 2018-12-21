import websocket as ws
from abc import abstractmethod
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import uuid
import json


class BaseWebsocket(object):
    ws_count = 0  # websocket connection nums.
    
    def __new__(cls, *args, **kwargs):
        cls.ws_count += 1
        if cls is _AuthWS:
            from .utils import ACCESS_KEY, SECRET_KEY
            if not (ACCESS_KEY and SECRET_KEY):
                raise Exception('No ACCESS_KEY or SECRET_KEY set exception!')
        return object.__new__(cls)

    def on_message(self, _msg):
        msg = json.loads(_msg)

    def send_message(self, msg):
        msg_json = json.dumps(msg).encode()
        self.ws.send(msg_json)

    def on_error(self, error):
        pass

    def on_close(self):
        if not self._active:
            return
        
        if self._reconn > 0:
            self.__start()
            self._reconn -= 1
            time.sleep(self._interval)
        else:
            self.__start()
            time.sleep(self._interval)

    def on_open(self):
        self._active = True

    @abstractmethod
    def pub_msg(self, msg):
        raise NotImplementedError

    def register_handler(self, handler):
        if handler not in self._handlers:
            self._handlers.append(handler)
            handler.start(self.name)

    def unregister_handler(self, handler):
        if handler in self._handlers:
            self._handlers.remove(handler)
            handler.stop(self.name)
    
    def __add__(self, handler):
        if isinstance(handler, BaseHandler):
            self.register_handler(handler)
        else:
            raise Exception('{handler} is not a Handler')
        return self

    def register_handler_func(self, topic):
        def _wrapper(_handler_func):
            if topic not in self._handle_funcs:
                self._handle_funcs[topic] = []
            self._handle_funcs[topic].append(_handler_func)
            return _handler_func
        return _wrapper

    @property
    def handlers(self):
        return self._handlers

    @property
    def handle_funcs(self):
        return self._handle_funcs
    
    def run(self):
        if not hasattr(self, 'ws_thread') or not self.ws_thread.is_alive():
            self.__start()

    def __start(self):
        self.ws = ws.WebSocketApp(
            self.addr,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws_thread = Thread(target=self.ws.run_forever, name=self.name)
        self.ws_thread.setDaemon(True)
        self.ws_thread.start()

    def stop(self):
        if hasattr(self, 'ws_thread') and self.ws_thread.is_alive():
            self._active = False
            self.ws.close()


class _CXWS(BaseWebsocket):
    def __init__(self, host='localhost', reconn=10, interval=3):
        self._protocol = 'wss://'
        self._host = host
        self._path = '/ws'
        self.addr = self._protocol + self._host + self._path
        self._threadPool = ThreadPoolExecutor(max_workers=3)
        self.name = f'ChuangXinWS_{uuid.uuid1()}'
        self._handlers = []
        self._handle_funcs = {}
        self._active = False
        self._reconn = reconn
        self._interval = interval

    def on_open(self):
        self._active = True
        pass

    def on_message(self, _msg):
        msg = json.loads(_msg)
        if 'ping' in msg:
            pong = {'pong': msg['ping']}
            self.send_message(pong)
        else:
            self.pub_msg(msg)

    def pub_msg(self, msg):
        topic = msg.get('target')
        for h in self._handle_funcs.get(topic, []):
            h(msg)