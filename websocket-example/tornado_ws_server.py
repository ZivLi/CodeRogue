import tornado
import tornado.websocket


class EchoWebSocket(tornado.websocket.WebSocketHandler):

    def open(self):
        print('WebSocket opened')

    def on_message(self, message):
        print(message)
        self.write_message('You said: ' + message)

    def on_close(self):
        print('WebSocket closed')


class SocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def open(self):
        SocketHandler.clients.add(self)

    def on_close(self):
        SocketHandler.clients.remove(self)


if __name__ == '__main__':
    app = tornado.web.Application([(r'/', EchoWebSocket),])
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
