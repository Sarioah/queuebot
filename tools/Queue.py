#!/usr/bin/python3
from tools.tList import tList

class Mthds():
    def __init__(self, parent):
        self.parent = parent
    
    def __getitem__(self, key): return getattr(self, key, None)

    def open(self, *a): 
        self.parent.isopen = True
        return "Random queue is now open!"

    def close(self, *a):
        self.parent.isopen = False
        return "Queue is now closed"

    def clear(self, *a):
        self.parent.entries, self.parent.current, self.parent.picked = tList(), {}, tList()
        return "Queue has been cleared"

    def currentsong(self, *a):
        if self.parent.current: return f"Current song is \"{trunc(self.parent.current['song'], ssl)}\", "\
                                       f"requested by {self.parent.current['user']}"
        else: return "Nothing's been played yet"

    def addsong(self, user, song, *a):
        if not self.parent: return f"Sorry {user}, the queue is closed"
        if not song: return f"@{user} please write a song name after !sr"
        oldsong = self.parent.entries[user]
        self.parent.entries[user] = song
        if oldsong: msg = f"{user}'s song changed from \"{trunc(oldsong, ssl // 2)}\" "\
                          f"to \"{trunc(song, ssl // 2)}\""
        else: msg = f"Added \"{trunc(song, ssl)}\" to the queue for {user}"
        return msg

    def leave(self, user, *a):
        if user in self.parent:
            del self.parent.entries[user]
            return f"{user}, you have left the queue"
        else: return f"{user}, you weren't in the queue"

    def removesong(self, _, index, *a):
        try: user, song = self.parent.entries.pop(int(index) - 1)
        except ValueError: return "Please specify a song number"
        except IndexError: return "Specified song doesn't exist"
        else: return f"Removed \"{trunc(song, ssl)}\" from the queue"

    def removeuser(self, _, user = "", *a):
        try:
            if user: del self.parent.entries[user]
            else: return "Please specify a username"
        except AttributeError: return "Please specify a username"
        except ValueError: return f"{user} is not in the queue"
        else: return f"Removed {user} from the queue"

    def status(self, user = "", *a):
        msg = f"Random queue is {'open' if self.parent else 'closed'}"

        if self.parent.entries: 
            msg += f" • There are {len(self.parent)} songs in the queue"
        else:
            msg += " • Queue is empty"

        if self.parent.entries[user]:
            msg += f" • {user} your song is \"{trunc(self.parent.entries[user], ssl)}\""

        return msg

    def listsongs(self, *a):
        if not self.parent.entries: return "Queue is empty"
        msg = "List of songs in the queue: "
        for i, (u, s) in enumerate(self.parent.entries): msg += f"{i + 1}. \"{trunc(s, msl)}\" • "
        return msg[:-3]

    def listusers(self, *a):
        if not self.parent.entries: return "Queue is empty"
        msg = "List of users in the queue: "
        for u, s in self.parent.entries: msg += f"{u}, "
        return msg[:-2]

    def played(self, *a):
        if not self.parent.picked: return "Nothing's been played yet"
        msg = "Songs already played: "
        for u, s in self.parent.picked: msg += f"\"{trunc(s, msl)}\", "
        return msg[:-2]

    def picksong(self, _, selection = 0, *a): 
        try:
            if selection: user, song = self.parent.entries.pop(int(selection) - 1)
            else: user, song = self.parent.entries.random(self.parent.picked)
        except ValueError:
            return "Please specify a song number"
        except IndexError as x:
            if str(x) == "pop index out of range": return "No such song"
            else: return "Queue is empty"
        else:
            self.parent.current["user"], self.parent.current["song"] = user, song
            self.parent.picked.append((user, song))
            return f"{user} was picked, their song was \"{trunc(song, msl)}\""

class Queue():
    def __init__(self, channel, *tuples):
        self.channel = channel
        self.isopen = False
        self.entries, self.current, self.picked = tList(*tuples), {}, tList()
        self.mthds = Mthds(self)

    def __bool__(self): return self.isopen
    def __contains__(self, user): return user in self.entries
    def __getitem__(self, attr): return getattr(self, attr, None)
    def __iter__(self): return self.entries.__iter__()
    def __len__(self): return len(self.entries)

ssl = 200 #single song length
msl = 35 #multi song length (for lists)

def trunc(msg, l):
    return msg if len(msg) <= l else msg[:l - 1] + "…"
