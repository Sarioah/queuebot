#!/usr/bin/python3
class Queue():
    def __init__(self, channel, *tuples):
        from tList import tList
        self.channel = channel
        self.isopen = False
        self.entries = tList(*tuples)
        self.current = {}
        self.picked = tList()
        print("init complete")

    def __bool__(self): return self.isopen
    def __contains__(self, user): return user in self.entries
    def __iter__(self): return self.entries.__iter__()

    def open(self): 
        self.isopen = True
        return "Random queue is now open!"

    def close(self):
        self.isopen = False
        return "Queue is now closed"

    def addsong(self, user, song):
        if not self: return "Sorry %s, the queue is closed" % user
        oldsong = self.entries[user]
        self.entries[user] = song
        if oldsong:
            msg = "%s's song changed from \"%s\" to \"%s\"" % (user, trunc(oldsong, ssl // 2), trunc(song, ssl // 2))
        else:
            msg = "Added \"%s\" to the queue for %s" % (trunc(song, ssl), user)
        return msg

    def removesong(self, index):
        try:
            user, song = self.entries.pop(index - 1)
        except IndexError:
            return "Specified song doesn't exist"
        else:
            return "Removed \"%s\" from the queue" % trunc(song, ssl)

    def removeuser(self, user):
        try:
            del self.entries[user]
        except ValueError:
            return "%s is not in the queue" % user
        else:
            return "Removed %s from the queue" % user

    def status(self, user = ""):
        msg = "Random queue is %s" % ("open" if self else "closed")

        if self.entries: 
            msg += " • There are %d songs in the queue" % len(self.entries)
        else:
            msg += " • Queue is empty"

        if self.entries[user]:
            msg += " • %s your song is \"%s\"" % (user, trunc(self.entries[user], ssl))

        return msg

    def listsongs(self):
        if not self.entries: return "Queue is empty"
        msg = "List of songs in the queue: "
        for i, (u, s) in enumerate(self.entries): msg += "%d.\"%s\" • " % (i + 1, trunc(s, msl))
        return msg[:-3]

    def listusers(self):
        if not self.entries: return "Queue is empty"
        msg = "List of users in the queue: "
        for u, s in self.entries: msg += "%s, " % u
        return msg[:-2]

    def played(self):
        if not self.picked: return "Nothing's been played yet"
        msg = "Songs already played: "
        for _, s in self.picked: msg += "\"%s\", " % trunc(s, msl)
        return msg[:-2]

    def picksong(self): 
        try:
            user, song = self.entries.random(self.picked)
        except IndexError:
            return "Queue is empty"
        else:
            self.current["user"], self.current["song"] = user, song
            self.picked.append((user, song))
            return "%s was picked, their song was \"%s\"" % (user, trunc(song, ssl))

ssl = 200 #single song length
msl = 35 #multi song length (for lists)

def trunc(msg, l):
    return msg if len(msg) <= l else msg[:l - 1] + "…"
