from icalendar import Event

class EventData():
    def __init__(self, vEvent = None):
        self.__vEvent = vEvent
        self.__isUpdated = False
        self.__idict = {}

    def __getattr__(self, item):
        if self.__vEvent is None:
            return self.item
        else:
            return self.__vEvent.get(item)

    def set_value(self, key, value):
        self.__idict[key] = value

    def to_VEvent(self):
        if self.__vEvent == None:
            self.__vEvent = Event()
            self.__vEvent['SEQUENCE'] = 1
            for key, value in self.__idict.items():
                self.__vEvent[key] = value
        else:
            for key, value in self.__idict.items():
                oldval = self.__vEvent.get(key)
                if oldval == None and value == None:
                    #nothing to set.
                    None
                elif oldval != value:
                    self.__vEvent[key] = value
                    if self.__isUpdated == False:
                        seq = self.__vEvent.get('SEQUENCE')
                        self.__vEvent['SEQUENCE'] = seq + 1
                        self.__isUpdated = True

        return self.__vEvent


