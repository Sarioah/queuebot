import threading

from irc_bot.events import HandleEvent
from tools.chat import CommandHandler
from tools.song_queue import SongQueue
from tools.highlight_string import Highlighter
from tools.highlight_string import find_strings


class MessageHandler:
    def __init__(self, channel, sep, trunc, logging, emotes):
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
        if self.logging:
            with open("messages.log", "a", encoding="UTF-8") as file:
                file.write(str(chat_msg) + "\n")

        msg = {}
        try:
            msg['msg'] = chat_msg.arguments[0]
        except IndexError:
            msg['msg'] = ""
        msg['words'] = msg['msg'].split(" ")
        msg['tags'] = {
            i['key']: i['value']
            for i in chat_msg.tags
        }
        msg['msg'] = self.handle_emotes(msg)

        return HandleEvent(msg)(msg_type, self.handle_command)

    def handle_command(self, msg, words, tags):
        if msg.startswith(self.sep):
            sender = tags['display-name']
            action = self.commandhandler.find_command(
                tags['badges'],
                words[0][1:],
                self.song_queue.mthds
            )
            if action:
                with self.lock:
                    res = action(
                        sender, " ".join(words[1:]),
                        self.emote_indices_short
                    )
                    self.song_queue.save()
                return res
        return None

    def handle_emotes(self, msg):
        try:
            twitch_indices = [
                (int(p.split('-')[0]), int(p.split('-')[1]) + 1)
                for t in msg['tags']['emotes'].split('/')
                for p in t.split(':')[1].split(',')
            ]
        except Exception:
            twitch_indices = []

        bttv_indices = find_strings(msg['msg'], self.emotes)
        emote_indices = list(set(bttv_indices + twitch_indices))

        adjustment = len(msg['words'][0]) + 1
        self.emote_indices_short = [
            (i - adjustment, j - adjustment)
            for (i, j) in emote_indices
        ]

        return Highlighter(True, msg['msg'], indices=emote_indices).get_highlight()
