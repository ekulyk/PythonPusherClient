class Channel(object):
    def __init__(self, channel_name):
        self.name = channel_name

        self.event_callbacks = {}

    def bind(self, event_name, callback):
        if event_name not in self.event_callbacks.keys():
            self.event_callbacks[event_name] = []

        self.event_callbacks[event_name].append(callback)

    def trigger(self, event_name, data):
        pass

    def _handle_event(self, event_name, data):
        if event_name in self.event_callbacks.keys():
            for callback in self.event_callbacks[event_name]:
                callback(data)
