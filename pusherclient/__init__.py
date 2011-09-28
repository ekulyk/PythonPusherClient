from channel import Channel
from connection import Connection

import hashlib, hmac
import time

import thread

class Pusher():
    def __init__(self, applicationKey, encryption=False, secret=None):
        self.channels = {}

        self.secret = secret

        self.host = "ws.pusherapp.com"
        self.encryption = encryption
        if self.encryption:
            self.protocol = "wss"
            self.port = "443"
        else:
            self.protocol = "ws"
            self.port = "80"

        self.applicationKey = applicationKey
        self.client_id = 'js'
        self.version = '1.7.1'
        self.path = "/app/%s?client=%s&version=%s" % (self.applicationKey,
                                                      self.client_id,
                                                      self.version)

        self.url = "%s://%s:%s/%s" % (self.protocol,
                                      self.host,
                                      self.port,
                                      self.path)

        self.connection = Connection(self._connectionHandler, self.url)

        thread.start_new_thread(self.connection._connect, ())

    def disconnect(self):
        pass

    def subscribe(self, channelName):
        if channelName not in self.channels.keys():
            authKey = self._generateAuthKey(channelName) 

            self.connection._send_event('pusher:subscribe',
                                        {'channel':channelName,
                                         'auth':authKey,
                                        }
                                       )

            self.channels[channelName] = Channel(channelName)

        return self.channels[channelName]

    def unsubscribe(self, channelName):
        if channelName in self.channel.keys():
            self.connection._send_event('pusher:unsubscribe',
                                        {'channel':channelName,
                                        }
                                       )
            del self.channels[channelName]

    def channel(self, channelName):
        channel = None

        if channelName in self.channels.keys():
            channel = self.channels[channelName]

        return channel        

    def wait_until_connected(self):
        while self.connection.state != "connected":
            time.sleep(1)

    def _connectionHandler(self, eventName, data, channelName):
        if channelName in self.channels.keys():
            self.channels[channelName]._handle_event(eventName, data)

    def _generateAuthKey(self, channelName):
        authKey = ""

        if self.secret:
            stringToSign = str(self.connection.socket_id) + ":" + str(channelName)
            h = hmac.new(self.secret, stringToSign, hashlib.sha256)

            authKey = "%s:%s" % (self.applicationKey, h.hexdigest())

        return authKey
