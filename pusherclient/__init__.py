from channel import Channel
from connection import Connection

import hashlib, hmac
import time

import thread

try:
    import simplejson as json
except:
    import json

class Pusher():
    def __init__(self, applicationKey, encryption=False, secret=None, userdata={}):
        self.channels = {}

        self.secret = secret

        self.userdata = userdata

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
        self.connection.disconnect()
        self.channels = {}

    def subscribe(self, channelName):
        if channelName not in self.channels.keys():
            data = {}
            data['channel'] = channelName

            if channelName.startswith('presence-'):
                authKey = self._generatePresenceAuthKey(self.connection.socket_id,
                                                        self.applicationKey,
                                                        channelName,
                                                        self.secret,
                                                        self.userdata)

                data['auth'] = authKey
                data['channel_data'] = json.dumps(self.userdata)
            elif channelName.startswith('private-'):
                authKey = self._generatePrivateAuthKey(self.connection.socket_id,
                                                       self.applicationKey,
                                                       channelName,
                                                       self.secret)

                data['auth'] = authKey
            else:
                authKey = ""

            self.connection._send_event('pusher:subscribe', data)

            self.channels[channelName] = Channel(channelName)

        return self.channels[channelName]

    def unsubscribe(self, channelName):
        if channelName in self.channels.keys():
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

    def _connectionHandler(self, eventName, data, channelName):
        if channelName in self.channels.keys():
            self.channels[channelName]._handle_event(eventName, data)


    def _generatePrivateAuthKey(self, socket_id,
                                      applicationKey,
                                      channelName,
                                      secret):
        authKey = ""

        if socket_id and applicationKey and channelName and secret:
            stringToSign = "%s:%s" % (socket_id, channelName)
            h = hmac.new(secret, stringToSign, hashlib.sha256)
            authKey = "%s:%s" % (applicationKey, h.hexdigest())

        return authKey


    def _generatePresenceAuthKey(self, socket_id,
                                       applicationKey,
                                       channelName,
                                       secret,
                                       userData):
        authKey = ""

        if socket_id and applicationKey and channelName and secret and userData:
            stringToSign = "%s:%s:%s" % (socket_id, channelName, json.dumps(userData))
            h = hmac.new(secret, stringToSign, hashlib.sha256)
            authKey = "%s:%s" % (applicationKey, h.hexdigest())

        return authKey
