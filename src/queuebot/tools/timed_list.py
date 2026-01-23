"""Manages a list erases its content after a specified time delay."""

from time import time


class TimedList:
    """Implements a TimedList.

    Erases its content if no writes occur within the specified delay.
    """

    default_delay = 600

    def __init__(self, delay=None, **kwargs):
        """Create the list.

        Args:
            delay: Time delay after which the list is cleared. Writes within
                this period keep extending the life of the list's data.
            kwargs: Collects attributes in a dict to apply to the newly created
                list.
        """
        self.data = kwargs.get("data", [])
        self.delay = kwargs.get("delay") or delay or TimedList.default_delay
        self.time = kwargs.get("time", time())

    def __bool__(self):
        """Return True if list contains data."""
        return bool(self.data)

    def __len__(self):
        """Return length of list."""
        return len(self.data)

    def __iter__(self):
        """Pass iter calls to list's data.

        Yields:
            Elements taken from the list.
        """
        for element in self.data:
            yield element

    def __contains__(self, value):
        """Return True if the given value appears in the list."""
        return value in self.data

    def __getitem__(self, index):
        """Return the list element at the specified index."""
        return self.data[index]

    def __getattribute__(self, attr):
        """Intercept attribute lookups in order to clear an expired list.

        If the list's data is outdated, clear it before returning the requested
        attribute.

        Args:
            attr (str): Name of the requested attribute.

        Returns:
            Content of the requested attribute.
        """
        delay = object.__getattribute__(self, "delay")
        if (
            attr == "data"
            and (now := time()) - object.__getattribute__(self, "time") > delay
        ):
            object.__setattr__(self, "time", now)
            object.__setattr__(self, "data", [])
        return object.__getattribute__(self, attr)

    def __setattr__(self, attr, value):
        """Intercept attribute writes in order to record the current timestamp.

        This timestamp is checked on later lookups to decide if the list needs
        clearing.

        Args:
            attr (str): Name of the attribute to write.
            value: Value to write to the given attribute.
        """
        if attr == "data":
            object.__setattr__(self, "time", time())
        object.__setattr__(self, attr, value)

    def append(self, value):
        """Add a value to the end of the list.

        Args:
            value: Value to add to the list.
        """
        self.time = time()
        self.data += [value]

    def get(self):
        """Return the stored list."""
        return self.data

    def serialise(self):
        """Express self in a format compatible with methods like json, str.

        Returns:
            dict: Attributes and their values
        """
        return self.__dict__
