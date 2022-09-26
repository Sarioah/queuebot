#!/usr/bin/python3
"""
Tools for managing a random or prioritised request queue

In Just Dance mode, the queue holds song choices, and picks users at random
(prioritising users who haven't been picked before)
In Jackbox mode, the queue holds usernames, and picks users FIFO (also
prioritising users who haven't been picked before)

Classes:
    BaseMethods: Class containing methods to manipulate all types of queues
    JDMethods: Class containing methods to manipulate Just Dance / random queues
    JBMethods: Class containing methods to manipulate Jackbox / priority queues
    SongQueue: Class containing users / requests

Functions:
    trunc: Take a string then truncate it to the specified length
"""

import time

from os import path
from json import loads, dumps
from traceback import format_exc

from tools.tuple_list import TupleList
from tools.timed_list import TimedList
from tools.text import colourise as c
from tools.text import Paginate


SINGLE_SONG_LENGTH = 200
MULTI_SONG_LENGTH = 50  # (for lists)


class BaseMethods:
    """Contain methods common to all types of queues"""
    def __init__(self, parent):
        self.parent = parent

    def __getitem__(self, key):
        return getattr(self, key, None)

    def close(self, *_args):
        """Close the queue, disallowing further entries"""
        self.parent.isopen = False
        return "Queue is now closed"

    def clear(self, *_args):
        """Remove all entries from the queue"""
        self.parent.current = {}
        self.parent.entries, self.parent.picked = TupleList(), TupleList()
        return "Queue has been cleared"

    def leave(self, sender, /, *_args):
        """Remove the sender's request from the queue"""
        if sender in self.parent:
            del self.parent.entries[sender]
            return f"{sender}, you have left the queue"
        return f"{sender}, you weren't in the queue"

    def listusers(self, _, page=1, /, *_args):
        """List all users who have a request in the queue"""
        if not self.parent.entries:
            return "Queue is empty"
        msg = "List of users in the queue: "
        for user, _song in self.parent.entries:
            msg += f"{user}, "
        return Paginate(msg[:-2], self.parent.msg_limit, ", ")[page]

    def removeuser(self, _, user="", /, *_args):
        """Remove the specified user from the queue"""
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

    def queueconfirm(self, *_args):
        """Confirm a prior "testqueue" command, then add the loaded data into the queue"""
        try:
            if time.time() - self.parent.testdata[1] < 10:
                self.parent.entries = TupleList(*self.parent.testdata[0])
                del self.parent.testdata
                return "Test data loaded into queue"
            del self.parent.testdata
        except AttributeError:
            pass
        return None

    def testqueue(self, *_args):
        """
        Load testing data from "testdata.json", ready to be added with "queueconfirm"

        Example file contents:
        [
            [
                "Test user 1",
                "Test user 1's request"
            ],
            [
                "Test user 2",
                "Test user 2's request"
            ]
        ]
        """
        if path.exists('testdata.json'):
            try:
                with open("testdata.json", "r", encoding="utf-8") as file_:
                    self.parent.testdata = [
                        loads(file_.read())
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
    """Contain methods used to manipulate Just Dance / random queues"""
    def jbqueue(self, *_args):
        """Change queue into Jackbox / priority mode"""
        self.parent.mthds = JBMethods(self.parent)
        return "Queue is now in jackbox mode"

    def jdqueue(self, *_args):
        """Change queue into Just Dance / random mode"""
        return "Queue is already in Just Dance mode"

    def open(self, *_args):
        """Open the queue, allowing new entries to be added"""
        self.parent.isopen = True
        return "Random queue is now open"

    def currententry(self, *_args):
        """List the last entry that was picked"""
        if self.parent.current:
            return (
                f"Current song is \"{trunc(self.parent.current['entry'], SINGLE_SONG_LENGTH)}"
                f"\", requested by {self.parent.current['user']}"
            )
        return "Nothing's been played yet"

    def addentry(self, sender, entry, emote_indices, /, *_args):
        """
        Add the sender's entry to the queue

        Blank entries not allowed in this mode
        """
        if not self.parent:
            return f"Sorry {sender}, the queue is closed"
        if not entry:
            return f"@{sender} please write a song name after !sr"

        emote_indices = list({
            i for j in emote_indices
            for i in j
        })

        if len(entry) in emote_indices:
            entry += " "
        if 0 in emote_indices:
            entry = " " + entry

        oldentry = self.parent.entries[sender]
        self.parent.entries[sender] = entry
        if oldentry:
            return (
                f"{sender}'s song changed from \"{trunc(oldentry, SINGLE_SONG_LENGTH // 2)}\" "
                f"to \"{trunc(entry, SINGLE_SONG_LENGTH // 2)}\""
            )
        return f"Added \"{trunc(entry, SINGLE_SONG_LENGTH)}\" to the queue for {sender}"

    def removeentry(self, _, index, /, *_args):
        """Remove the sender's entry from the queue"""
        try:
            _user, entry = self.parent.entries.pop(int(index) - 1)
        except ValueError:
            return "Please specify a song number"
        except IndexError:
            return "Specified song doesn't exist"
        else:
            return f"Removed \"{trunc(entry, SINGLE_SONG_LENGTH)}\" from the queue"

    def status(self, sender, /, *_args):
        """
        List the status of the queue

        Shows whether the queue is open / closed, how many requests there are,
        as well as the sender's current request (if applicable)
        """
        msg = f"Random queue is {'open' if self.parent else 'closed'}"

        if self.parent.entries:
            msg += f" • There are {len(self.parent)} songs in the queue"
        else:
            msg += " • Queue is empty"

        if self.parent.entries[sender]:
            msg += (
                f" • {sender} your song is "
                f"\"{trunc(self.parent.entries[sender], SINGLE_SONG_LENGTH)}\""
            )
        return msg

    def listentries(self, _, page=1, /, *_args):
        """List all entries currently in the queue"""
        if not self.parent.entries:
            return "Queue is empty"
        msg = "List of songs in the queue: "
        for i, (_user, song) in enumerate(self.parent.entries):
            msg += f"{i + 1}. \"{trunc(song, MULTI_SONG_LENGTH)}\" • "
        return Paginate(msg[:-3], self.parent.msg_limit, " • ")[page]

    def picked(self, _, page=1, /, *_args):
        """List all entries that have been picked so far"""
        if not self.parent.picked:
            return "Nothing's been played yet"
        msg = "Songs already played: "
        for _user, song in self.parent.picked:
            msg += f"\"{trunc(song, MULTI_SONG_LENGTH)}\", "
        return Paginate(msg[:-2], self.parent.msg_limit, ", ")[page]

    def pickentry(self, _, selection=0, /, *_args):
        """
        Pick an entry from the queue

        If a number is specified, pick that entry directly

        If no entry is specified, pick an entry at random. Entries from users not in the
        picked list are chosen first
        """
        try:
            if selection:
                user, song = self.parent.entries.pop(int(selection) - 1)
                repeat_pick = user in self.parent.picked
            else:
                (user, song), repeat_pick = (
                    self.parent.entries.random(self.parent.picked)
                )
        except ValueError:
            return "Please specify a song number"
        except IndexError as exc:
            if str(exc) == "pop index out of range":
                return "No such song"
            return "Queue is empty"
        else:
            self.parent.current["user"], self.parent.current["entry"] = (
                user, song
            )
            self.parent.picked.append((user, song))
            return (
                f"{user} was picked{' again' if repeat_pick else ''}, "
                f"their song was \"{trunc(song, SINGLE_SONG_LENGTH)}\""
            )


class JBMethods(BaseMethods):
    """Contains methods used to manipulate Jackbox / priority queues"""
    def jbqueue(self, *_args):
        """Change queue to Jackbox / priority mode"""
        return "Queue is already in Jackbox mode"

    def jdqueue(self, *_args):
        """Change queue to Just Dance / random mode"""
        self.parent.mthds = JDMethods(self.parent)
        return "Queue changed to Just Dance mode"

    def open(self, *_args):
        """Open the queue, allowing new entries to be added"""
        self.parent.isopen = True
        return "Priority queue is now open"

    def currententry(self, *_args):
        """List the last entry to be picked"""
        if self.parent.currentusers:
            res = "Currently picked users: " + " • ".join([
                f"{index + 1}. {user}"
                for (index, user) in enumerate(self.parent.currentusers)
            ])
            return trunc(res, SINGLE_SONG_LENGTH)
        return "No-one's been picked yet"

    def addentry(self, sender, /, *_args):
        """
        Add the sender to the queue

        if the sender has already been picked, insert their entry after any new users

        The request itself is set to the sender's name
        """
        if not self.parent:
            return f"Sorry {sender}, the queue is closed"
        if sender in self.parent.entries:
            msg = (
                f"@{sender} you are already in the queue at position "
                f"{self.parent.entries.index(sender) + 1}"
            )
        else:
            self.parent.entries[sender] = sender
            self.parent.entries = self.parent.entries.deprioritise(
                self.parent.picked
            )
            msg = (
                f"Added {sender} to the queue at position "
                f"{self.parent.entries.index(sender) + 1}"
            )
        return msg

    def removeentry(self, _, index, /, *_args):
        """Remove the sender from the queue"""
        try:
            user, _entry = self.parent.entries.pop(int(index) - 1)
        except ValueError:
            return "Please specify an entry"
        except IndexError:
            return "Specified entry doesn't exist"
        else:
            return f"Removed {user} from the queue"

    def status(self, sender="", /, *_args):
        """
        List the status of the queue
        Shows whether the queue is open / closed, how many users there are,
        as well as the sender's current position in the queue
        """
        msg = f"Priority queue is {'open' if self.parent else 'closed'}"

        if self.parent.entries:
            msg += f" • There are {len(self.parent)} users in the queue"
        else:
            msg += " • Queue is empty"

        if self.parent.entries[sender]:
            msg += (
                f" • @{sender} you are in the queue at position "
                f"{self.parent.entries.index(sender) + 1}"
            )

        return msg

    def listentries(self, _, page=1, /, *_args):
        """List all users currently in the queue"""
        if not self.parent.entries:
            return "Queue is empty"
        msg = "List of users in the queue: "
        for i, (user, _entry) in enumerate(self.parent.entries):
            msg += f"{i + 1}. {user} • "
        return Paginate(msg[:-3], self.parent.msg_limit, " • ")[page]

    def picked(self, _, page=1, /, *_args):
        """List all users that have been picked so far"""
        if not self.parent.picked:
            return "No-one's been picked yet"
        msg = "Users already picked: "
        for user, _entry in self.parent.picked:
            msg += f"{user}, "
        return Paginate(msg[:-2], self.parent.msg_limit, ", ")[page]

    def pickentry(self, _, selection=0, /, *_args):
        """
        Pick a user from the queue

        If a number is specified, pick that user specifically

        If no user is specified, pick the first user in the queue
        """
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
        except IndexError as exc:
            if str(exc) == "pop index out of range":
                return "No such user"
            return "Queue is empty"
        else:
            self.parent.current["user"], self.parent.current["entry"] = (
                user, entry
            )
            self.parent.picked.append((user, entry))
            self.parent.currentusers.append(user)
            return (
                f"Get ready to play, @{user}, you were picked from the "
                f"queue{' again!' if repeat_pick else '!'}"
            )


class SongQueue:
    """Main class to hold all data relating to a request queue"""
    def __init__(self, channel, *tuples):
        self.channel = None
        self.isopen = None
        self.current = None
        self.currentusers = None
        self.entries = None
        self.picked = None
        self.msg_limit = 499 - len(channel)
        self.mthds = JDMethods(self)
        self.load(channel, *tuples)

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
        """Create the queue from scratch"""
        self.channel = channel
        self.isopen = True
        self.current, self.entries, self.picked = {}, TupleList(*tuples), TupleList()
        self.currentusers = TimedList(600)
        self.save()

    def save(self):
        """Dump all queue data to a file in the data/ folder"""
        with open(f"data/{self.channel}.json", "w", encoding="utf-8") as file_:
            res = {}
            res["channel"] = self.channel
            res["isopen"] = self.isopen
            res["current"] = self.current
            res["currentusers"] = self.currentusers.serialise()
            res["entries"] = self.entries.serialise()
            res["picked"] = self.picked.serialise()
            file_.write(dumps(res, indent=4))

    def load(self, channel, *tuples):
        """
        Load existing queue data from file

        Create queue from scratch if data can't be loaded
        """
        try:
            with open(f"data/{channel}.json", "r", encoding="utf-8") as file_:
                res = loads(file_.read())
                self.channel = res["channel"]
                self.isopen = res["isopen"]
                self.current = res["current"]
                self.currentusers = TimedList(**res["currentusers"])
                self.entries = TupleList(*res["entries"])
                self.picked = TupleList(*res["picked"])
        except Exception:
            print(c(
                f"\n{format_exc()}\n"
                "Failed to load saved queue, creating new one",
                "GREY"
            ))
            self.new(channel, *tuples)


def trunc(msg, length):
    """
    Take a string and truncate it to the specfied length

    Arguments:
        msg: the input string
        length: the length to truncate the input string to

    Returns:
        the truncated string, ending in the ellipses character if truncation occurred
    """
    return msg if len(msg) <= length else msg[:length - 1] + "…"
