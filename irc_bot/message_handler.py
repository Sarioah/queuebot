"""
MessageHandler that manages a SongQueue, selects methods based on a given message object,
and generates responses by processing the message using the selected method
"""
import threading

from irc_bot.events import HandleEvent
from tools.chat import CommandHandler
from tools.song_queue import SongQueue
from tools.highlight_string import Highlighter
from tools.highlight_string import find_strings


class MessageHandler:
    """The main MessageHandler class"""

    def __init__(self, channel, sep, trunc, logging, emotes):
        """
        Create a MessageHandler

        Args:
            channel: the channel name to create the SongQueue against

            sep: command separator, if a message starts with this string then the following word
                shall be treated as a command

            trunc: function used to truncate long messages

            logging: whether to log all received messages to file

            emotes: list of lists of strings that shall be treated as emotes, alongside the
                emote designations listed in the message for native twitch emotes
        """
        self.sep = sep
        self.channel = channel
        self.emotes = sum(emotes.values(), start=[])
        self.emote_indices_short = []
        self.commandhandler = CommandHandler()
        self.song_queue = SongQueue(self.channel)
        self.lock = threading.Lock()
        self.logging = bool(logging == "True")
        self.trunc = trunc

    def handle_msg(self, chat_msg, msg_type="pubmsg"):
        """Handle a given message"""
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
        msg["msg"] = self.handle_emotes(msg)

        return HandleEvent(msg)(msg_type, self.handle_command)

    def handle_command(self, msg, words, tags):
        """
        Check a message for the command separator. If found, then search the SongQueue for an
        appropriate method to process the message with
        """
        if msg.startswith(self.sep):
            sender = tags["display-name"]
            action = self.commandhandler.find_command(
                tags["badges"], words[0][1:], self.song_queue.mthds
            )
            if action:
                with self.lock:
                    res = action(sender, " ".join(words[1:]), self.emote_indices_short)
                    self.song_queue.save()
                return res
        return None

    def handle_emotes(self, msg):
        """
        Check a message to see if it contains any emote strings. If found, colourise the message
        around each emote
        """
        try:
            twitch_indices = [
                (int(p.split("-")[0]), int(p.split("-")[1]) + 1)
                for t in msg["tags"]["emotes"].split("/")
                for p in t.split(":")[1].split(",")
            ]
        except Exception:
            twitch_indices = []

        bttv_indices = find_strings(msg["msg"], self.emotes)
        emote_indices = list(set(bttv_indices + twitch_indices))

        adjustment = len(msg["words"][0]) + 1
        self.emote_indices_short = [(i - adjustment, j - adjustment) for (i, j) in emote_indices]

        return Highlighter(True, msg["msg"], indices=emote_indices).get_highlight()
