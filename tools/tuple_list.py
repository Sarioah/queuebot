"""A dict-like object that maintains ordering of key: value pairs."""

import random


class TupleList:
    """A dict - like object that also maintains ordering of key: value pairs.

    Addressing by key is case - insensitive

    Implements simple mathematical operators as set - like interactions
    """

    def __init__(self, *tuples):
        """Create the TupleList.

        Args:
            tuples: Collection of 2-tuples representing key: value pairs.
        """
        self.data = []
        for key, value in tuples:
            self.data.append((key, value))

    def __str__(self):
        """Return contents of list as a string."""
        res = "\n".join(f'{key}: "{value}"' for key, value in self.data)
        return f"TupleList contents:\n{res}"

    def __repr__(self):
        """Return contents of list as an eval compatible string."""
        res = ", ".join(f'("{key}", "{value}")' for key, value in self.data)
        return f"TupleList({res})"

    def __bool__(self):
        """Return True if list contains data."""
        return bool(self.data)

    def __contains__(self, key):
        """Return presence of key in list."""
        return key.casefold() in [k.casefold() for (k, v) in self.data]

    def __delitem__(self, key):
        """Delete the given key and its value from the list."""
        del self.data[self.index(key)]

    def __len__(self):
        """Return length of list."""
        return len(self.data)

    def __iter__(self):
        """Yield tuples from the list."""
        for i in self.data:
            yield i

    def __getitem__(self, key):
        """Return the value associated with the given key.

        Key lookups are case-insensitive, returns None if key is not found.

        Args:
            key: Key to search for

        Returns:
            Value associated with the key if it exists, otherwise None.
        """
        if key.casefold() in self:
            return {k.casefold(): v for k, v in self.data}[key.casefold()]
        return None

    def __setitem__(self, key, value):
        """Set the value for the given key."""
        if key not in self:
            self.data.append((key, value))
        else:
            for i, (k, _) in enumerate(self.data):
                if k.casefold() == key.casefold():
                    self.data[i] = (key, value)
                    break

    def __add__(self, other):
        """Return result of adding two TupleLists.

        Accepts another TupleList. Values from second TupleList added to the
        first, any common values are taken from the second TupleList.

        Args:
            other: The other list to add to self.

        Returns:
            Result of the addition, as a new TupleList.
        """
        res = self.copy()
        for (key, value) in other:
            res[key] = value
        return res

    def __sub__(self, other):
        """Return result of subtracting two TupleLists.

        Accepts another TupleList. If the first TupleList contains keys present
        in the second, remove them.

        Args:
            other: The other list to subtract from self.

        Returns:
            Result of the subtraction, as a new TupleList.
        """
        res = TupleList()
        for (key, value) in self:
            if key not in other:
                res.append((key, value))
        return res

    def __iadd__(self, other):
        """Return result of an in-place addition."""
        return self + other

    def __isub__(self, other):
        """Return result of an in-place subtraction."""
        return self - other

    def __eq__(self, other):
        """Return equality between two TupleLists."""
        return repr(self) == repr(other)

    def append(self, item):
        """Append a tuple to the end of the TupleList."""
        return self.data.append(item)

    def copy(self):
        """Return a new TupleList containing the same data as self."""
        return TupleList(*self.data)

    def deprioritise(self, other=None):
        """Move the keys found in the other TupleList to the end of self."""
        if other is None:
            other = TupleList()
        front = self - other
        back = self - front
        return front + back

    def index(self, key):
        """Return the index of the given key."""
        return [k.casefold() for (k, v) in self.data].index(key.casefold())

    def random(self, other="", first=False):
        """Return a key: value pair at random.

        If another TupleList is provided, prefer to pick keys unique to the
        first TupleList if possible, otherwise pick a random key: value pair.

        Args:
            other (TupleList): Keys in this list are considered last when
                picking.
            first (bool): If true, don't pick randomly, but instead return the
                first key: value unique to the first list.

        Returns:
            2-tuple ((key, value), repeat_pick), where the first element is the
            key: value pair picked. The second element is True when the picked
            key was present in the supplied "other" TupleList argument.
        """
        # TODO: Refactor this mess
        if not other:
            other = TupleList()
        pool = self - other
        if pool:
            repeat_pick = False
        else:
            repeat_pick = True
            pool = self
        if first:
            key, _ = pool.data[0]
        else:
            key, _ = random.choice(pool.data)
        return self.pop(self.index(key)), repeat_pick

    def pop(self, index):
        """Remove the given tuple index from self and return it."""
        return self.data.pop(index)

    def serialise(self):
        """Return the list of tuples stored in self."""
        return self.data.copy()
