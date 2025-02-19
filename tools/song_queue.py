#!/usr/bin/python3
"""Tools for managing a random or prioritised request queue.

In Just Dance / random mode, the queue holds song choices, and picks users at
random (prioritising users who haven't been picked before)
In Jackbox / priority mode, the queue holds usernames, and picks users FIFO
(also prioritising users who haven't been picked before)

Classes:
    BaseMethods: Class containing methods to manipulate all types of queues
    JDMethods: Class containing methods to manipulate Just Dance / random
        queues.
    JBMethods: Class containing methods to manipulate Jackbox / priority queues
    SongQueue: Class containing users / requests

Functions:
    trunc: Take a string then truncate it to the specified length
"""
import asyncio
import contextlib
import time
from asyncio import TimeoutError
from json import dumps, loads
from os import path
from traceback import format_exc

import aiohttp
from aiohttp.client_exceptions import ClientError
from aiohttp.http_websocket import WebSocketError
from aiohttp.streams import EofStream

from tools.text import colourise as c, Paginate
from tools.timed_list import TimedList
from tools.tuple_list import TupleList

SINGLE_SONG_LENGTH = 200
MULTI_SONG_LENGTH = 50  # (for lists)


class BaseMethods:
    """Methods common to all types of queues."""

    def __init__(self, parent):
        """Initialise object.

        Args:
            parent: Parent object containing the data most of these methods
                operate on.
        """
        self.parent = parent
        self.exclusions = []

    def __getitem__(self, key):
        """Return method that matches the given key."""
        return getattr(self, key, None)

    def close(self, *_args):
        """Close the queue, disallowing further entries."""
        self.parent.isopen = False
        return "Queue is now closed"

    def clear(self, *_args):
        """Remove all entries from the queue."""
        self.parent.current, self.parent.currentusers = {}, TimedList(600)
        self.parent.entries, self.parent.picked = TupleList(), TupleList()
        return "Queue has been cleared"

    def leave(self, sender, /, *_args):
        """Remove the sender's request from the queue."""
        if sender in self.parent:
            del self.parent.entries[sender]
            return f"{sender}, you have left the queue"
        return f"{sender}, you weren't in the queue"

    def listusers(self, _, page=1, /, *_args):
        """List all users who have a request in the queue."""
        if not self.parent.entries:
            return "Queue is empty"
        msg = "List of users in the queue: "
        for user, _song in self.parent.entries:
            msg += f"{user}, "
        return Paginate(msg[:-2], self.parent.msg_limit, ", ")[page]

    def removeuser(self, _, user="", /, *_args):
        """Remove the specified user from the queue."""
        try:
            if user:
                del self.parent.entries[user]
            else:
                return "Please specify a username"
        except AttributeError:
            return "Please specify a username"
        except ValueError:
            return f'"{user}" is not in the queue'
        else:
            return f"Removed {user} from the queue"

    def queueconfirm(self, *_args):
        """Confirm a prior "testqueue" command.

        Adds the loaded data into the queue.

        Args:
            _args: Ignore extra positional args.

        Returns:
            Message string if data was loaded successfully, otherwise None.
        """
        max_age = 10
        with contextlib.suppress(AttributeError):
            if time.time() - self.parent.testdata[1] < max_age:
                self.parent.entries = TupleList(*self.parent.testdata[0])
                del self.parent.testdata
                return "Test data loaded into queue"
            del self.parent.testdata
        return None

    def testqueue(self, _, url=None, *_args):
        """Load testing data from testdata.json or an url provided as argument.

        Queue remains untouched until the load is confirmed with
        "queueconfirm".

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

        Args:
            url: Optional URL to load JSON queue data from
            _args: Ignore extra positional args.

        Returns:
            Message string with result of the load operation.
        """
        if url:
            try:
                self.parent.testdata = [loads(_get(url))]
            except ValueError as exc:
                return f"Error parsing webpage response: {exc}"
        elif path.exists("testdata.json"):
            try:
                with open("testdata.json", "r", encoding="utf-8") as file_:
                    self.parent.testdata = [loads(file_.read())]
            except (OSError, ValueError):
                return "Failed to load test data from file"
        else:
            return "No test data found"

        self.parent.testdata += [time.time()]
        return (
            "Test data loaded, do !queueconfirm within "
            "10 seconds to overwrite the current queue entries"
        )


class JDMethods(BaseMethods):
    """Methods used to manipulate Just Dance / random queues."""

    def __init__(self, parent):
        """Initialise object.

        Args:
            parent: Parent object containing the data most of these methods
                operate on.
        """
        super().__init__(parent)
        self.exclusions = [
            "join",
            "clearparty",
            "currentparty",
            "currentgroup",
            "currentuser",
            "currentusers",
        ]
        self.parent.mode = "random"

    def jbqueue(self, *_args):
        """Change queue into Jackbox / priority mode."""
        self.parent.mthds = JBMethods(self.parent)
        return "Queue is now in priority / user queue mode"

    @staticmethod
    def jdqueue(*_args):
        """Change queue into Just Dance / random song mode."""
        return "Queue is already in random song mode"

    def open(self, *_args):
        """Open the queue, allowing new entries to be added."""
        self.parent.isopen = True
        return "Random song queue is now open, type !sr <song name> to join!"

    def currententry(self, *_args):
        """List the last entry that was picked."""
        if self.parent.current:
            return (
                f"Current song is \"{trunc(self.parent.current['entry'], SINGLE_SONG_LENGTH)}"
                f"\", requested by {self.parent.current['user']}"
            )
        return "Nothing's been picked yet"

    def addentry(self, sender, entry, emote_indices, /, *_args):
        """Add the sender's entry to the queue.

        Blank entries not allowed in this mode. If the sender already had an
        entry in the queue, then change their entry to the new one.

        Args:
            sender: Username that sent the command.
            entry: Username's entry to add to the queue.
            emote_indices: List of 2-tuples representing where in the entry any
                emotes appear. Used to decide if a space needs to be added
                before or after the entry.
            _args: Ignore extra positional args.

        Returns:
            Message string with result of add / change operation.
        """
        if not self.parent:
            return f"Sorry {sender}, the queue is closed"
        if not entry:
            return f"@{sender} please write a song name after !sr"

        emote_indices = list({i for j in emote_indices for i in j})

        if len(entry) in emote_indices:
            entry += " "
        if 0 in emote_indices:
            entry = " " + entry

        old_entry = self.parent.entries[sender]
        self.parent.entries[sender] = entry
        if old_entry:
            return (
                f'{sender}\'s song changed from "{trunc(old_entry, SINGLE_SONG_LENGTH // 2)}" '
                f'to "{trunc(entry, SINGLE_SONG_LENGTH // 2)}"'
            )
        return f'Added "{trunc(entry, SINGLE_SONG_LENGTH)}" to the queue for {sender}'

    def removeentry(self, _, index, /, *_args):
        """Remove the sender's entry from the queue."""
        try:
            _user, entry = self.parent.entries.pop(int(index) - 1)
        except ValueError:
            return "Please specify a song number"
        except IndexError:
            return "Specified song doesn't exist"
        else:
            return f'Removed "{trunc(entry, SINGLE_SONG_LENGTH)}" from the queue'

    def status(self, sender, /, *_args):
        """List the status of the queue.

        Shows whether the queue is open / closed, how many requests there are,
        as well as the sender's current request (if applicable).

        Args:
            sender: Username that sent the command.
            _args: Ignore extra positional args.

        Returns:
            Message string with the status of the queue.
        """
        msg = f"Random queue is {'open' if self.parent else 'closed'}"

        if self.parent.entries:
            msg += f" • There are {len(self.parent)} songs in the queue"
        else:
            msg += " • Queue is empty"

        if self.parent.entries[sender]:
            msg += (
                f" • {sender} your song is "
                f'"{trunc(self.parent.entries[sender], SINGLE_SONG_LENGTH)}"'
            )
        return msg

    def listentries(self, _, page=1, /, *_args):
        """List all entries currently in the queue."""
        if not self.parent.entries:
            return "Queue is empty"
        msg = "List of songs in the queue: "
        for i, (_user, song) in enumerate(self.parent.entries):
            msg += f'{i + 1}. "{trunc(song, MULTI_SONG_LENGTH)}" • '
        return Paginate(msg[:-3], self.parent.msg_limit, " • ")[page]

    def picked(self, _, page=1, /, *_args):
        """List all entries that have been picked so far."""
        if not self.parent.picked:
            return "Nothing's been played yet"
        msg = "Songs already played: "
        for _user, song in self.parent.picked:
            msg += f'"{trunc(song, MULTI_SONG_LENGTH)}", '
        return Paginate(msg[:-2], self.parent.msg_limit, ", ")[page]

    def pickentry(self, _, selection=0, /, *_args):
        """Pick an entry from the queue.

        If a number is specified, pick that entry directly. If no entry is
        specified, pick an entry at random. Entries from users not in the
        picked list are chosen first.

        Args:
            _: Disregard sender
            selection: Specified entry number to pick. If omitted, pick one
                randomly.
            _args: Ignore extra positional args.

        Returns:
            Message string with the user and their song if picked, otherwise a
            message describing any issues with the specified selection.
        """
        try:
            if selection:
                user, song = self.parent.entries.pop(int(selection) - 1)
                repeat_pick = user in self.parent.picked
            else:
                (user, song), repeat_pick = self.parent.entries.random(
                    self.parent.picked
                )
        except ValueError:
            return "Please specify a song number"
        except IndexError as exc:
            if str(exc) == "pop index out of range":
                return "No such song"
            return "Queue is empty"
        else:
            self.parent.current["user"], self.parent.current["entry"] = (user, song)
            self.parent.picked.append((user, song))
            return (
                f"{user} was picked{' again' if repeat_pick else ''}, "
                f'their song was "{trunc(song, SINGLE_SONG_LENGTH)}"'
            )

    def lookupentry(self, _, search="", /, *_args):
        """Search queue for the given song.

        Args:
            _: Disregard sender
            search: Search string to look for.
            _args: Ignore extra positional args.

        Returns:
            String containing the first username whose song contains the search
            string.
        """
        for index, (user, song) in enumerate(self.parent):
            if song.casefold().find(search.casefold()) != -1:
                return (
                    f'{user} requested "{trunc(song, SINGLE_SONG_LENGTH)}" '
                    f"at position {index+1}"
                )
        return f'Song "{search}" not found in the queue'

    def lookupuser(self, _, search="", /, *_args):
        """Search queue for the given user.

        Args:
            _: Disregard sender
            search: User to look for.
            _args: Ignore extra positional args.

        Returns:
            String containing the user's song, if found in the queue.
        """
        search = search.replace("@", "")
        for index, (user, song) in enumerate(self.parent):
            if user.casefold().find(search.casefold()) != -1:
                return (
                    f'{user}\'s song is "{trunc(song, SINGLE_SONG_LENGTH)}", '
                    f'at position {index + 1}"'
                )
        return f'"{search}" is not in the queue'


class JBMethods(BaseMethods):
    """Methods used to manipulate Jackbox / priority queues."""

    def __init__(self, parent):
        """Initialise object.

        Args:
            parent: Parent object containing the data most of these methods
                operate on.
        """
        super().__init__(parent)
        self.exclusions = [
            "sr",
            "removesong",
            "whichsong",
            "whichuser",
        ]
        self.parent.mode = "priority"

    @staticmethod
    def jbqueue(*_args):
        """Change queue to Jackbox / priority mode."""
        return "Queue is already in priority / user queue mode"

    def jdqueue(self, *_args):
        """Change queue to Just Dance / random mode."""
        self.parent.mthds = JDMethods(self.parent)
        return "Queue changed to random song mode"

    def open(self, *_args):
        """Open the queue, allowing new entries to be added."""
        self.parent.isopen = True
        return "Priority queue is now open, type !join to join!"

    def clearparty(self, *_args):
        """Clear the current user party."""
        self.parent.currentusers = TimedList(600)
        return "Current user party has been cleared"

    def currententry(self, _, page=1, /, *_args):
        """List the users picked for the current party.

        List expires after ten minutes.

        Args:
            _: Disregard sender
            page: Page number of output to return.
            _args: Ignore extra positional args.

        Returns:
            Message string with the current party, if it exists.
        """
        if self.parent.currentusers:
            res = "Currently picked users: " + " • ".join(
                [
                    f"{index + 1}. {user}"
                    for (index, user) in enumerate(self.parent.currentusers)
                ]
            )
            return Paginate(res, self.parent.msg_limit, " • ")[page]
        return "No-one's been picked yet"

    def addentry(self, sender, /, *_args):
        """Add the sender to the queue.

        if the sender has already been picked, insert their entry after any new
        users. The request itself is set to the sender's name.

        Args:
            sender: Username that sent the command.
            _args: Ignore extra positional args.

        Returns:
            Message string with result of the add. Specifies the sender's
            current position in the queue.
        """
        if not self.parent:
            return f"Sorry {sender}, the queue is closed"
        if sender in self.parent:
            msg = (
                f"@{sender} you are already in the queue at position "
                f"{self.parent.entries.index(sender) + 1}"
            )
        else:
            self.parent.entries[sender] = sender
            self.parent.entries = self.parent.entries.deprioritise(self.parent.picked)
            msg = (
                f"Added {sender} to the queue at position "
                f"{self.parent.entries.index(sender) + 1}"
            )
        return msg

    def removeentry(self, _, index, /, *_args):
        """Remove the user at the specified position from the queue."""
        try:
            user, _entry = self.parent.entries.pop(int(index) - 1)
        except ValueError:
            return "Please specify an entry"
        except IndexError:
            return "Specified entry doesn't exist"
        else:
            return f"Removed {user} from the queue"

    def status(self, sender="", /, *_args):
        """List the status of the queue.

        Shows whether the queue is open / closed, how many users there are, as
        well as the sender's current position in the queue.

        Args:
            sender: Username that sent the command.
            _args: Ignore extra positional args.

        Returns:
            Message string with the status of the queue.
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
        """List all users currently in the queue."""
        if not self.parent.entries:
            return "Queue is empty"
        msg = "List of users in the queue: "
        for i, (user, _entry) in enumerate(self.parent.entries):
            msg += f"{i + 1}. {user} • "
        return Paginate(msg[:-3], self.parent.msg_limit, " • ")[page]

    def picked(self, _, page=1, /, *_args):
        """List all users that have been picked so far."""
        if not self.parent.picked:
            return "No-one's been picked yet"
        msg = "Users already picked: "
        for user, _entry in self.parent.picked:
            msg += f"{user}, "
        return Paginate(msg[:-2], self.parent.msg_limit, ", ")[page]

    def pickentry(self, _, selection=0, /, *_args):
        """Pick a user from the queue.

        If a number is specified, pick that user specifically. If no user is
        specified, pick the first user in the queue.

        Args:
            _: Disregard sender
            selection: Specified user number to pick. If omitted, pick the
                first one.
            _args: Ignore extra positional args.

        Returns:
            Message string with the picked user. Otherwise, a message
                describing any issues with the selection number.
        """
        try:
            if selection:
                user, entry = self.parent.entries.pop(int(selection) - 1)
                repeat_pick = user in self.parent.picked
            else:
                (user, entry), repeat_pick = self.parent.entries.random(
                    self.parent.picked, first=True
                )
        except ValueError:
            return "Please specify a user number"
        except IndexError as exc:
            if str(exc) == "pop index out of range":
                return "No such user"
            return "Queue is empty"
        else:
            self.parent.current["user"], self.parent.current["entry"] = (user, entry)
            self.parent.picked.append((user, entry))
            self.parent.currentusers.append(user)
            return (
                f"Get ready to play, @{user}, you were picked from the "
                f"queue{' again!' if repeat_pick else '!'}"
            )


class SongQueue:
    """Data relating to a song / request queue."""

    def __init__(self, channel, *tuples):
        """Initialise the SongQueue.

        Args:
            channel: Name of the channel the queue refers to.
            tuples: Username, song pairs to insert into the queue
        """
        self.channel = None
        self.isopen = None
        self.current = None
        self.currentusers = None
        self.entries = None
        self.picked = None
        self.mode = None
        self.msg_limit = 499 - len(channel)
        self.mthds = None
        self.load(channel, *tuples)

    def __bool__(self):
        """Return if queue is open or not."""
        return self.isopen

    def __contains__(self, user):
        """Return presence of user in the song queue."""
        return user in self.entries

    def __getitem__(self, attr):
        """Return attribute that matches the given key."""
        return getattr(self, attr, None)

    def __iter__(self):
        """Return iterator over the song queue."""
        return self.entries.__iter__()

    def __len__(self):
        """Return length of the song queue."""
        return len(self.entries)

    def new(self, channel, *tuples):
        """Create a new SongQueue instead of loading existing data.

        Args:
            channel: Name of the channel the queue refers to.
            tuples: Username, song pairs to insert into the queue.
        """
        self.channel = channel
        self.isopen = True
        self.mthds = JDMethods(self)
        self.current, self.entries, self.picked = {}, TupleList(*tuples), TupleList()
        self.currentusers = TimedList(600)
        self.save()

    def save(self):
        """Dump all queue data to a file in the data/ folder."""
        with open(f"data/{self.channel}.json", "w", encoding="utf-8") as file_:
            res = {
                "channel": self.channel,
                "isopen": self.isopen,
                "current": self.current,
                "mode": self.mode,
                "currentusers": self.currentusers.serialise(),
                "entries": self.entries.serialise(),
                "picked": self.picked.serialise(),
            }
            file_.write(dumps(res, indent=4))

    def load(self, channel, *tuples):
        """Load existing queue data from file.

        Create queue from scratch if data can't be loaded.

        Args:
            channel: Name of the channel the queue refers to.
            tuples: Username, song pairs to insert into the queue.
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
                if res["mode"] == "random":
                    self.mthds = JDMethods(self)
                else:
                    self.mthds = JBMethods(self)
        except (OSError, ValueError, LookupError):
            print(
                c(
                    f"\n{format_exc()}\nFailed to load saved queue, creating new one",
                    "GREY",
                )
            )
            self.new(channel, *tuples)


def trunc(msg, length):
    """Take a string and truncate it to the specified length.

    Args:
        msg: Input string.
        length: Length to truncate the input string to.

    Returns:
        Truncated string, ending in the ellipses character if truncation
        occurred.
    """
    return msg if len(msg) <= length else msg[: length - 1] + "…"


def _get(url):
    async def runner(url):
        try:
            async with aiohttp.ClientSession(read_timeout=3) as session:
                return await (await session.get(url)).text()
        except (ClientError, WebSocketError, EofStream, TimeoutError) as exc:
            raise ValueError(f"Error accessing webpage: {exc}")

    return asyncio.run(runner(url))
