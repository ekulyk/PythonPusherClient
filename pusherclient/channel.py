

class Channel():
    def __init__(self, channelName):
        self.name = channelName

        self.event_callbacks = {}


    def bind(self, eventName, callback):
        if eventName not in self.event_callbacks.keys():
            self.event_callbacks[eventName] = []

        self.event_callbacks[eventName].append(callback)

    def trigger(self, eventName, data):
        pass

    def _handle_event(self, eventName, data):
        if eventName in self.event_callbacks.keys():
            for callback in self.event_callbacks[eventName]:
                callback(data)
