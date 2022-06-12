#!/usr/bin/python3
import time
from os import path
from json import loads, dumps

from tools.tList import tList
from tools.text import colourise as c
from tools.text import paginate as p


class BaseMethods():

    def __init__(self, parent):
        self.parent = parent

    def __getitem__(self, key):
        return getattr(self, key, None)

    def close(self, *a):
        self.parent.isopen = False
        return "Queue is now closed"

    def clear(self, *a):
        self.parent.current = {}
        self.parent.entries, self.parent.picked = tList(), tList()
        return "Queue has been cleared"

    def leave(self, user, *a):
        if user in self.parent:
            del self.parent.entries[user]
            return f"{user}, you have left the queue"
        else:
            return f"{user}, you weren't in the queue"

    def listusers(self, user, page=1, *a):
        if not self.parent.entries:
            return "Queue is empty"
        msg = "List of users in the queue: "
        for u, s in self.parent.entries:
            msg += f"{u}, "
        return p(msg[:-2], self.parent.msg_limit, ", ")[page]

    def removeuser(self, _, user="", *a):
        try:
            if user:
                del self.parent.entries[user]
            else:
                return "Please specify a username"
        except AttributeError:
            return "Please specify a username"
        except ValueError:
            return f"{user} is not in the queue"
        else:
            return f"Removed {user} from the queue"

    def queueconfirm(self, *a):
        try:
            if time.time() - self.parent.testdata[1] < 10:
                self.parent.entries = tList(*self.parent.testdata[0])
                del(self.parent.testdata)
                return "Test data loaded into queue"
            else:
                del(self.parent.testdata)
        except AttributeError:
            return

    def testqueue(self, *a):
        if path.exists('testdata.json'):
            try:
                self.parent.testdata = [
                    loads(
                        open(
                            'testdata.json', 'r', encoding='utf-8'
                            ).read()
                        )
                    ]
            except Exception:
                return "Failed to load test data"
            else:
                self.parent.testdata += [time.time()]
                return (
                    "Test data loaded from file, do !queueconfirm within "
                    "10 seconds to overwrite the current queue entries"
                    )
        else:
            return "No test data file found "


class JDMethods(BaseMethods):

    def jbqueue(self, *a):
        self.parent.mthds = JBMethods(self.parent)
        return "Queue is now in jackbox mode"

    def jdqueue(self, *a):
        return "Queue is already in Just Dance mode"

    def open(self, *a):
        self.parent.isopen = True
        return "Random queue is now open"

    def currententry(self, *a):
        if self.parent.current:
            return (
                f"Current song is \"{trunc(self.parent.current['entry'], ssl)}"
                f"\", requested by {self.parent.current['user']}"
                )
        else:
            return "Nothing's been played yet"

    def addentry(self, user, entry, emote_indices, *a):
        if not self.parent:
            return f"Sorry {user}, the queue is closed"
        if not entry:
            return f"@{user} please write a song name after !sr"

        emote_indices = list(
            set([
                i for j in emote_indices
                for i in j
                ])
            )
        if len(entry) in emote_indices:
            entry += " "
        if 0 in emote_indices:
            entry = " " + entry

        oldentry = self.parent.entries[user]
        self.parent.entries[user] = entry
        if oldentry:
            msg = (
                f"{user}'s song changed from \"{trunc(oldentry, ssl // 2)}\" "
                f"to \"{trunc(entry, ssl // 2)}\""
                )
        else:
            msg = f"Added \"{trunc(entry, ssl)}\" to the queue for {user}"
        return msg

    def removeentry(self, _, index, *a):
        try:
            user, entry = self.parent.entries.pop(int(index) - 1)
        except ValueError:
            return "Please specify a song number"
        except IndexError:
            return "Specified song doesn't exist"
        else:
            return f"Removed \"{trunc(entry, ssl)}\" from the queue"

    def status(self, user="", *a):
        msg = f"Random queue is {'open' if self.parent else 'closed'}"

        if self.parent.entries:
            msg += f" • There are {len(self.parent)} songs in the queue"
        else:
            msg += " • Queue is empty"

        if self.parent.entries[user]:
            msg += (
                f" • {user} your song is "
                f"\"{trunc(self.parent.entries[user], ssl)}\""
                )

        return msg

    def listentries(self, user, page=1, *a):
        if not self.parent.entries:
            return "Queue is empty"
        msg = "List of songs in the queue: "
        for i, (u, e) in enumerate(self.parent.entries):
            msg += f"{i + 1}. \"{trunc(e, msl)}\" • "
        return p(msg[:-3], self.parent.msg_limit, " • ")[page]

    def picked(self, user, page=1, *a):
        if not self.parent.picked:
            return "Nothing's been played yet"
        msg = "Songs already played: "
        for u, e in self.parent.picked:
            msg += f"\"{trunc(e, msl)}\", "
        return p(msg[:-2], self.parent.msg_limit, ", ")[page]

    def pickentry(self, _, selection=0, *a):
        try:
            if selection:
                user, entry = self.parent.entries.pop(int(selection) - 1)
                repeat_pick = user in self.parent.picked
            else:
                (user, entry), repeat_pick = (
                    self.parent.entries.random(self.parent.picked)
                    )
        except ValueError:
            return "Please specify a song number"
        except IndexError as x:
            if str(x) == "pop index out of range":
                return "No such song"
            else:
                return "Queue is empty"
        else:
            self.parent.current["user"], self.parent.current["entry"] = (
                user, entry
                )
            self.parent.picked.append((user, entry))
            return (
                f"{user} was picked{' again' if repeat_pick else ''}, "
                f"their song was \"{trunc(entry, ssl)}\""
                )


class JBMethods(BaseMethods):

    def jbqueue(self, *a):
        return "Queue is already in Jackbox mode"

    def jdqueue(self, *a):
        self.parent.mthds = JDMethods(self.parent)
        return "Queue changed to Just Dance mode"

    def open(self, *a):
        self.parent.isopen = True
        return "Priority queue is now open"

    def currententry(self, *a):
        if self.parent.current:
            return (
                f"Current player is {trunc(self.parent.current['user'], ssl)}"
                )
        else:
            return "No-one's been picked yet"

    def addentry(self, user, *a):
        if not self.parent:
            return f"Sorry {user}, the queue is closed"
        if user in self.parent.entries:
            msg = (
                f"@{user} you are already in the queue at position "
                f"{self.parent.entries.index(user) + 1}"
                )
        else:
            self.parent.entries[user] = user
            self.parent.entries = self.parent.entries.deprioritise(
                self.parent.picked
                )
            msg = (
                f"Added {user} to the queue at position "
                f"{self.parent.entries.index(user) + 1}"
                )
        return msg

    def removeentry(self, _, index, *a):
        try:
            user, entry = self.parent.entries.pop(int(index) - 1)
        except ValueError:
            return "Please specify an entry"
        except IndexError:
            return "Specified entry doesn't exist"
        else:
            return f"Removed {user} from the queue"

    def status(self, user="", *a):
        msg = f"Priority queue is {'open' if self.parent else 'closed'}"

        if self.parent.entries:
            msg += f" • There are {len(self.parent)} users in the queue"
        else:
            msg += " • Queue is empty"

        if self.parent.entries[user]:
            msg += (
                f" • @{user} you are in the queue at position "
                f"{self.parent.entries.index(user) + 1}"
                )

        return msg

    def listentries(self, user, page=1, *a):
        if not self.parent.entries:
            return "Queue is empty"
        msg = "List of users in the queue: "
        for i, (u, e) in enumerate(self.parent.entries):
            msg += f"{i + 1}. {u} • "
        return p(msg[:-3], self.parent.msg_limit, " • ")[page]

    def picked(self, user, page=1, *a):
        if not self.parent.picked:
            return "No-one's been picked yet"
        msg = "Users already picked: "
        for u, e in self.parent.picked:
            msg += f"{u}, "
        return p(msg[:-2], self.parent.msg_limit, ", ")[page]

    def pickentry(self, _, selection=0, *a):
        try:
            if selection:
                user, entry = self.parent.entries.pop(int(selection) - 1)
                repeat_pick = user in self.parent.picked
            else:
                (user, entry), repeat_pick = (
                    self.parent.entries.random(self.parent.picked, first=True)
                    )
        except ValueError:
            return "Please specify a user number"
        except IndexError as x:
            if str(x) == "pop index out of range":
                return "No such user"
            else:
                return "Queue is empty"
        else:
            self.parent.current["user"], self.parent.current["entry"] = (
                user, entry
                )
            self.parent.picked.append((user, entry))
            return (
                f"Get ready to play, @{user}, you were picked from the "
                f"queue{' again!' if repeat_pick else '!'}"
                )


class Queue():

    def __init__(self, channel, *tuples):
        self.load(channel, *tuples)
        self.msg_limit = 499 - len(channel)
        self.mthds = JDMethods(self)

    def __bool__(self):
        return self.isopen

    def __contains__(self, user):
        return user in self.entries

    def __getitem__(self, attr):
        return getattr(self, attr, None)

    def __iter__(self):
        return self.entries.__iter__()

    def __len__(self):
        return len(self.entries)

    def new(self, channel, *tuples):
        self.channel = channel
        self.isopen = True
        self.current, self.entries, self.picked = {}, tList(*tuples), tList()
        self.save()

    def save(self):
        with open(
                "data/%s.json" % self.channel,
                "w", encoding="utf-8"
                ) as f:
            res = {}
            res["channel"] = self.channel
            res["isopen"] = self.isopen
            res["current"] = self.current
            res["entries"] = self.entries.serialise()
            res["picked"] = self.picked.serialise()
            f.write(dumps(res, indent=4))

    def load(self, channel, *tuples):
        try:
            with open(
                    "data/%s.json" % channel,
                    "r", encoding="utf-8"
                    ) as f:
                res = loads(f.read())
                self.channel = res["channel"]
                self.isopen = res["isopen"]
                self.current = res["current"]
                self.entries = tList(*res["entries"])
                self.picked = tList(*res["picked"])
        except Exception:
            import sys
            from traceback import format_exception
            tb = ''.join(
                    format_exception(
                        *sys.exc_info()
                        )
                    )
            print(c(
                f"\n{tb}\n"
                "Failed to load saved queue, creating new one",
                "GREY"
                ))
            self.new(channel, *tuples)


def trunc(msg, L):
    return msg if len(msg) <= L else msg[:L - 1] + "…"


ssl = 200  # single song length
msl = 50  # multi song length (for lists)
