class EventData():
    def __init__(self, vEvent):
        self.__vEvent = vEvent
        self.__isUpdated = False

        self.genre = None
    def __getattr__(self, item):
        if self.__vEvent is None:
            return self.item
        else:
            return self.__vEvent.get(item)