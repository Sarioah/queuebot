#!/usr/bin/python3

class tList():
    """Implements a dict - like object that also maintains
    ordering of key: value pairs

    Addressing by key is case - insensitive

    Implements simple mathematical operators as set - like interactions"""
    def __init__(self, *tuples):
        """key: value pairs should be passed in as a collection of tuples"""
        self.data = []
        for item in tuples:
            self.data.append(item)

    def __str__(self):
        msg = "tList contents:\n"
        for k, v in self.data:
            msg += "%s: \"%s\"\n" % (k, v)
        return msg[:-1]

    def __repr__(self):
        msg = ""
        for k, v in self.data:
            msg += "(\"%s\", \"%s\"), " % (k, v)
        return "tList(%s)" % msg[:-2]

    def __bool__(self):
        return True if self.data else False

    def __contains__(self, key):
        return key.lower() in [
            k.lower()
            for (k, v) in self.data
            ]

    def __delitem__(self, key):
        del self.data[self.index(key)]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for i in self.data:
            yield i

    def __getitem__(self, key):
        if key.lower() in self:
            return {
                k.lower(): v
                for k, v in self.data
                }[key.lower()]

    def __setitem__(self, key, value):
        if key not in self:
            self.data.append((key, value))
        else:
            for i, (k, v) in enumerate(self.data):
                if k.lower() == key.lower():
                    self.data[i] = (key, value)
                    break

    def __add__(self, other):
        """Accepts another tList.
        Values from second tList added to the first, any common values are
        taken from the second tList"""
        res = self.copy()
        for (key, value) in other:
            res[key] = value
        return res

    def __sub__(self, other):
        """Accepts another tList.
        If the first tList contains keys present in the second, remove them"""
        res = tList()
        for (key, value) in self:
            if key not in other:
                res.append((key, value))
        return res

    def __iadd__(self, other):
        return self + other

    def __isub__(self, other):
        return self - other

    def append(self, item):
        return self.data.append(item)

    def copy(self):
        return tList(*self.data)

    def index(self, key):
        return [
            k.lower()
            for (k, v) in self.data
            ].index(key.lower())

    def random(self, other="", first=False):
        """Picks a key: value pair at random.
        If another tList is provided, prefer to pick keys unique to
        the first tList if possible"""
        from random import choice
        if not other:
            other = tList()
        pool = self - other
        if pool:
            repeat_pick = False
        else:
            repeat_pick = True
            pool = self
        if first:
            key, value = pool.data[0]
        else:
            key, value = choice(pool.data)
        return self.pop(self.index(key)), repeat_pick

    def pop(self, index):
        return self.data.pop(index)

    def serialise(self):
        return [
            (k, v)
            for k, v in self.data
            ]
