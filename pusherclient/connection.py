import websocket
try:
    import simplejson as json
except:
    import json

from threading import Thread, Timer
import time
import logging


class Connection(Thread):
    def __init__(self, eventHandler, url, logLevel=logging.INFO):
        self.socket = None

        self.socket_id = ""

        self.eventCallbacks = {}

        self.eventHandler = eventHandler

        self.url = url

        self.needsReconnect = False
        self.reconnectInterval = 10

        self.pongReceived = False
        self.pongTimeout = 5

        self.bind("pusher:connection_established", self._connect_handler)
        self.bind("pusher:connection_failed", self._failed_handler)
        self.bind("pusher:pong", self._pong_handler)

        self.state = "initialized"

        self.logger = logging.getLogger()
        self.logger.addHandler(logging.StreamHandler())
        if logLevel == logging.DEBUG:
            websocket.enableTrace(True)
        self.logger.setLevel(logLevel)

        # From Martyn's comment at: https://pusher.tenderapp.com/discussions/problems/36-no-messages-received-after-1-idle-minute-heartbeat
        #   "We send a ping every 5 minutes in an attempt to keep connections 
        #   alive..."
        # This is why we set the connection timeout to 5 minutes, since we can
        # expect a pusher heartbeat message every 5 minutes.  Adding 5 sec to
        # account for small timing delays which may cause messages to not be
        # received in exact 5 minute intervals.
        self.connectionTimeout = 305
        self.connectionTimer = Timer(self.connectionTimeout, self._connectionTimedOut)

        self.pingInterval = 115
        self.pingTimer = Timer(self.pingInterval, self._send_ping)
        self.pingTimer.start()

        Thread.__init__(self)

    def bind(self, stateEvent, callback):
        if stateEvent not in self.eventCallbacks.keys():
            self.eventCallbacks[stateEvent] = []

        self.eventCallbacks[stateEvent].append(callback)

    def disconnect(self):
        self.needsReconnect = False
        self.socket.close()

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
        self.connectionTimer.start()

    def _on_error(self, ws, error):
        self.logger.info("Connection: Error - %s" % error)
        self.state = "failed"
        self.needsReconnect = True

    def _on_message(self, ws, message):
        self.logger.info("Connection: Message - %s" % message)

        # Stop our timeout timer, since we got some data
        self.connectionTimer.cancel()
        self.pingTimer.cancel()

        params = self._parse(message)

        if 'event' in params.keys():
            if 'channel' not in params.keys():
                # We've got a connection event.  Lets handle it.
                if params['event'] in self.eventCallbacks.keys():
                    for callback in self.eventCallbacks[params['event']]:
                        callback(params['data'])
                else:
                    self.logger.info("Connection: Unhandled event")
            else:
                # We've got a channel event.  Lets pass it up to the pusher
                # so it can be handled by the appropriate channel.
                self.eventHandler(params['event'], 
                                  params['data'], 
                                  params['channel'])

        # We've handled our data, so restart our connection timeout handler
        self.connectionTimer = Timer(self.connectionTimeout, self._connectionTimedOut)
        self.connectionTimer.start()

        self.pingTimer = Timer(self.pingInterval, self._send_ping)
        self.pingTimer.start()

    def _on_close(self, ws):
        self.logger.info("Connection: Connection closed")
        self.state = "disconnected"

    def _parse(self, message):
        return json.loads(message)

    def _send_event(self, eventName, data):
        self.socket.send(json.dumps({'event':eventName, 'data':data}))

    def _send_ping(self):
        self.logger.info("Connection: ping to pusher")
        self.socket.send(json.dumps({'event':'pusher:ping', 'data':''}))
        self.pongTimer = Timer(self.pongTimeout, self._check_pong)
        self.pongTimer.start()

    def _check_pong(self):
        self.pongTimer.cancel()
        if (self.pongReceived == True):
            self.pongReceived = False
        else:
            self.logger.info("Did not receive pong in time.  Will attempt to reconnect.")
            self.state = "failed"
            self.needsReconnect = True
            self.socket.close()


    def _connect_handler(self, data):
        parsed = json.loads(data)

        self.socket_id = parsed['socket_id']

        self.state = "connected"

    def _failed_handler(self, data):
        parsed = json.loads(data)

        self.state = "failed"

    def _pong_handler(self, data):
	# self. logger.info("Connection: pong from pusher")
        self.pongReceived = True

    def _connectionTimedOut(self):
        self.logger.info("Did not receive any data in time.  Reconnecting.")
        self.state = "failed"
        self.needsReconnect = True
        self.socket.close()
