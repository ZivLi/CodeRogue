import tornado
from tornado.websocket import websocket_connect


class WSClient(object):

    def __init__(self, url):
        self.url = url
        self.ioloop = tornado.ioloop.IOLoop.current()

    def start(self):
        websocket_connect(
            self.url,
            self.ioloop,
            callback=self.on_connected,
            on_message_callback=self.on_message)
        self.ioloop.start()

    def on_connected(self, f):
        try:
            conn = f.result()
            conn.write_message('hello')
        except Exception as e:
            print(e)
            self.ioloop.stop()

    def on_message(self, msg):
        print(msg)
        if msg.endswith('hello'):
            self.ioloop.stop()

if __name__ == '__main__':
    wsc = WSClient('ws://localhost:8000')
