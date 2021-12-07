#!/usr/bin/python3

class tList():
    def __init__(self, *tuples):
        self.data = []
        for item in tuples: self.data.append(item)

    def __str__(self):
        msg = "tList contents:\n"
        for i in self.data: msg += "%s: \"%s\"\n" % i
        return msg[:-1]

    def __repr__(self):
        msg = ""
        for i in self.data: msg += "(\"%s\", \"%s\"), " % i
        return "tList(%s)" % msg[:-2]

    def __bool__(self): return True if self.data else False
    
    def __iter__(self):
        for i in self.data: yield i

    def __contains__(self, key): return key.lower() in [k.lower() for (k, v) in self.data]
    
    def __len__(self): return len(self.data)

    def __getitem__(self, key):
        if key.lower() in self: return {k.lower(): v for (k, v) in self.data}[key.lower()]

    def __setitem__(self, key, value):
        if key not in self: self.data.append((key, value))
        else: 
            for i, (k, v) in enumerate(self.data):
                if k.lower() == key.lower():
                    self.data[i] = ((key, value))
                    break

    def __delitem__(self, key): del self.data[self.index(key)]

    def __add__(self, other):
        res = self.copy()
        for (key, value) in other: res[key] = value
        return res

    def __iadd__(self, other): return self + other

    def __sub__(self, other):
        res = tList()
        for (key, value) in self:
            if key not in other: res.append((key, value))
        return res
    
    def __isub__(self, other): return self - other

    def copy(self): return tList(*self.data)

    def index(self, key): return [k.lower() for (k, v) in self.data].index(key.lower())

    def pop(self, index): return self.data.pop(index)

    def append(self, item): return self.data.append(item)

    def random(self, other = tList()):
        from random import choice
        pool = self - other or self
        key, value = choice(pool.data)
        return self.pop(self.index(key))
