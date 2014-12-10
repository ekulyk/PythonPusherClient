try:
    import simplejson as json
except ImportError:
    import json

# Python >3.4
#from autobahn.asyncio.websocket import WebSocketServerProtocol

# Python 2.7
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

class PusherServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Server: onConnect")

    def onOpen(self):
        print("Server: onOpen")
        self.sendEvent('pusher:connection_established', data={'socket_id':'testid'})

    def onMessage(self, payload, isBinary):
        print("Server: onMessage")

        payload = json.loads(payload)

        self.handleEvent(payload)

    def onClose(self, wasClean, code, reason):
        print("Server: onClose")

    def sendEvent(self, event, data='', channel=None):
        print "Server: sendEvent %s" % event

        message = {
            'event': event,
            'data': json.dumps(data)
        }

        if channel is not None:
            message['channel'] = channel

        self.sendMessage(json.dumps(message))

    def handleEvent(self, payload):
        if 'event' in payload:
            if payload['event'] == 'pusher:ping':
                self.sendEvent('pusher:pong')
            elif payload['event'] == 'pusher:subscribe':
                if ('data' in payload) and ('channel' in payload['data']):
                    ## For testing send a test message on subscription
                    if payload['data']['channel'] == 'test_channel':
                        self.sendEvent('test_event', {'message': 'test'}, 'test_channel')
            else:
                pass
        else:
            pass

class Pusher():
    def __init__(self, port=9000):
        self.factory = WebSocketServerFactory()
        self.factory.protocol = PusherServerProtocol

        self.port = port

    def run(self):
        reactor.listenTCP(self.port, self.factory)
        reactor.run()

    def stop(self, fromThread = False):
        if fromThread:
            reactor.callFromThread(reactor.stop)
        else:
            reactor.stop()

