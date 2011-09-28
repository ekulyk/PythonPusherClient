import websocket
try:
    import simplejson as json
except:
    import json

from threading import Thread
import time
import logging

CONNECTION_EVENTS_NEW = [
                         'initialized',
                         'connecting',
                         'connected',
                         'unavailable',
                         'failed',
                         'disconnected',
                        ]

CONNECTION_EVENTS_OLD = [
                         'pusher:connection_established',
                         'pusher:connection_failed',
                        ]

class Connection(Thread):
    def __init__(self, eventHandler, url, logLevel=logging.INFO):
        self.socket = None

        self.socket_id = ""

        self.eventCallbacks = {}

        self.eventHandler = eventHandler

        self.url = url

        self.needsReconnect = False
        self.reconnectInterval = 10

        self.bind("pusher:connection_established", self._connect_handler)
        self.bind("pusher:connection_failed", self._failed_handler)

        self.state = "initialized"

        self.logger = logging.getLogger()
        self.logger.addHandler(logging.StreamHandler())
        if logLevel == logging.DEBUG:
            websocket.enableTrace(True)
        self.logger.setLevel(logLevel)

        Thread.__init__(self)

    def bind(self, stateEvent, callback):
        if stateEvent not in self.eventCallbacks.keys():
            self.eventCallbacks[stateEvent] = []

        self.eventCallbacks[stateEvent].append(callback)

    def run(self):
        self._connect()

    def _connect(self):
        self.state = "connecting"

        self.socket = websocket.WebSocketApp(self.url, 
                                             self._on_open, 
                                             self._on_message,
                                             self._on_error,
                                             self._on_close)

        self.socket.run_forever()

        while (self.needsReconnect):
            self.logger.info("Attempting to connect again in %s seconds." % self.reconnectInterval)
            self.state = "unavailable"
            time.sleep(self.reconnectInterval)
            self.socket.run_forever()

    def _on_open(self, ws):
        self.logger.info("Connection: Connection opened")

    def _on_error(self, ws, error):
        self.logger.info("Connection: Error - %s" % error)
        self.state = "failed"
        self.needsReconnect = True

    def _on_message(self, ws, message):
        self.logger.info("Connection: Message - %s" % message)

        params = self._parse(message)

        if 'event' in params.keys():
            if (params['event'] in CONNECTION_EVENTS_NEW) or (params['event'] in CONNECTION_EVENTS_OLD):

                if params['event'] in self.eventCallbacks.keys():
                    for callback in self.eventCallbacks[params['event']]:
                        callback(params['data'])
            else:
                if 'channel' in params.keys():
                    self.eventHandler(params['event'], 
                                      params['data'], 
                                      params['channel'])
                else:
                    self.logger.info("Connection: Unknown event type")

    def _on_close(self, ws):
        self.logger.info("Connection: Connection closed")
        self.state = "disconnected"

    def _parse(self, message):
        return json.loads(message)

    def _send_event(self, eventName, data):
        self.socket.send(json.dumps({'event':eventName, 'data':data}))

    def _connect_handler(self, data):
        parsed = json.loads(data)

        self.socket_id = parsed['socket_id']

        self.state = "connected"

    def _failed_handler(self, data):
        parsed = json.loads(data)

        self.state = "failed"
