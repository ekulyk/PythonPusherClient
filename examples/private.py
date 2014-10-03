#!/usr/bin/env python

import sys
sys.path.append('..')

import time

import pusherclient

global pusher

def print_usage(filename):
    print("Usage: python %s <appkey> <secret>" % filename)

def channel_callback(data):
    print("Channel Callback: %s" % data)

def connect_handler(data):
    channel = pusher.subscribe("private-channel")

    channel.bind('my_event', channel_callback)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print_usage(sys.argv[0])
        sys.exit(1)

    appkey = sys.argv[1]
    secret = sys.argv[2]

    pusher = pusherclient.Pusher(appkey, secret=secret)

    pusher.connection.bind('pusher:connection_established', connect_handler)
    pusher.connect()

    while True:
        time.sleep(1)
