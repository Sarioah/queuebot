"""
Manages a list object, that erases its list content after a specified time
"""
from time import time


class TimedList():
    """
    Implements a TimedList that erases its content if no writes occur within
    the specified delay
    """
    default_delay = 600

    def __init__(self, delay=None, **kwargs):
        self.data = kwargs.get("data", [])
        self.delay = kwargs.get("delay") or delay or TimedList.default_delay
        self.time = kwargs.get("time", time())

    def __bool__(self):
        return bool(self.data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for element in self.data:
            yield element

    def __contains__(self, value):
        return value in self.data

    def __getitem__(self, index):
        return self.data[index]

    def __getattribute__(self, attr):
        delay = object.__getattribute__(self, "delay")
        if (now := time()) - object.__getattribute__(self, "time") > delay:
            object.__setattr__(self, "time", now)
            object.__setattr__(self, "data", [])
        return object.__getattribute__(self, attr)

    def __setattr__(self, attr, value):
        object.__setattr__(self, "time", time())
        object.__setattr__(self, attr, value)

    def append(self, value):
        """Add a value to the end of the list"""
        self.time = time()
        self.data += [value]

    def get(self):
        """Return content of the stored list"""
        return self.data

    def serialise(self):
        """Express self in a format compatible with existing methods like json, str"""
        return self.__dict__
