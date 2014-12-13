# Python 2.7
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory


class Pusher():
    def __init__(self, protocol, port=9000):
        self.factory = WebSocketServerFactory()
        self.factory.protocol = protocol

        self.port = port

    def run(self):
        reactor.listenTCP(self.port, self.factory)
        reactor.run()

    def stop(self, fromThread = False):
        if fromThread:
            reactor.callFromThread(reactor.stop)
        else:
            reactor.stop()

