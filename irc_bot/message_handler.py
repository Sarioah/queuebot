"""Classes used for handling messages and generating appropriate responses.

Classes:
    MessageHandler: MessageHandler that manages a SongQueue, selects response
        methods based on a given message object, generates responses by
        processing the message using the selected method.
"""

import threading

from irc_bot.events import HandleEvent
from tools.chat import CommandHandler
from tools.highlight_string import find_strings, Highlighter
from tools.song_queue import SongQueue


class MessageHandler:
    """Handler to generate responses from messages."""

    def __init__(self, channel, sep, trunc, logging, emotes):
        """Create a MessageHandler.

        Args:
            channel: Channel name to create the SongQueue against.
            sep: Command separator, if a message starts with this string then
                the following word shall be treated as a command.
            trunc: Function used to truncate long messages.
            logging: Whether to log all received messages to file.
            emotes: List of lists of strings that shall be treated as emotes,
                in addition to the emote designations listed in the message
                for native twitch emotes.
        """
        self.sep = sep
        self.channel = channel
        self.emotes = [emote for emote_list in emotes.values() for emote in emote_list]
        self.emote_indices_short = []
        self.command_handler = CommandHandler()
        self.song_queue = SongQueue(self.channel)
        self.lock = threading.Lock()
        self.logging = bool(logging == "True")
        self.trunc = trunc

    def handle_msg(self, chat_msg, msg_type="pubmsg"):
        """Handle a given message.

        Extract message text and tags from the Event object passed in from an
        IRC connection.

        Args:
            chat_msg (irc.client.Event):
                Message to process.
            msg_type: Type of message that should be processed by this handler.

        Returns:
            Response string generated by the HandleEvent object.
        """
        if self.logging:
            with open("messages.log", "a", encoding="UTF-8") as file:
                file.write(str(chat_msg) + "\n")

        msg = {}
        try:
            msg["msg"] = chat_msg.arguments[0]
        except IndexError:
            msg["msg"] = ""
        msg["words"] = msg["msg"].split(" ")
        msg["tags"] = {i["key"]: i["value"] for i in chat_msg.tags}
        # noinspection PyTypeChecker
        msg["msg"] = self.handle_emotes(msg)

        return HandleEvent(msg)(msg_type, self.handle_command)

    def handle_command(self, msg, words, tags):
        """Check if a message represents a command, then execute it.

        First check the message for the command separator. If found, then
        search the SongQueue for an appropriate method to process the message
        with.

        Args:
            msg: Message string to search through.
            words: List of words in the message.
            tags: Tags attached to the original message Event object.

        Returns:
            None or string with a response generated by the command.
        """
        if msg.startswith(self.sep):
            sender = tags["display-name"]
            action = self.command_handler.find_command(
                tags["badges"], words[0][1:], self.song_queue.mthds
            )
            if action:
                with self.lock:
                    res = action(sender, " ".join(words[1:]), self.emote_indices_short)
                    self.song_queue.save()
                return res
        return None

    def handle_emotes(self, msg: dict):
        """Check a message to see if it contains any emote strings.

        If found, colourise the message around each emote.

        Args:
            msg (irc.client.Event):
                Message to process.

        Returns:
            String containing any applicable colour codes around emote strings.
        """
        try:
            twitch_indices = [
                (int(p.split("-")[0]), int(p.split("-")[1]) + 1)
                for t in msg["tags"]["emotes"].split("/")
                for p in t.split(":")[1].split(",")
            ]
        except AttributeError:
            twitch_indices = []

        bttv_indices = find_strings(msg["msg"], self.emotes)
        emote_indices = list(set(bttv_indices + twitch_indices))

        adjustment = len(msg["words"][0]) + 1
        self.emote_indices_short = [
            (i - adjustment, j - adjustment) for (i, j) in emote_indices
        ]

        return Highlighter(True, msg["msg"], indices=emote_indices).get_highlight()
