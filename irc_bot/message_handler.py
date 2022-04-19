import threading
import shelve

from irc_bot.events import handle_event
from tools.chat import CommandHandler
from tools.Queue import Queue
from tools.highlight_string import highlighter


class message_handler:

    def __init__(self, channel, sep, trunc, logging, emotes):
        self.sep = sep
        self.channel = channel
        self.emotes = sum(emotes.values(), start=[])
        self.commandhandler = CommandHandler()
        self.shelve = shelve.open(
                f"data/{self.channel}.db", "c",
                writeback=True
                )
        if self.channel not in self.shelve:
            self.shelve[self.channel] = Queue(self.channel)
        self.lock = threading.Lock()
        self.logging = True if logging == "True" else False
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

        return handle_event(msg)(msg_type, self.handle_command)

    def handle_command(self, msg, words, tags):
        if msg.startswith(self.sep):
            sender = tags['display-name']
            action = self.commandhandler.find_command(
                    tags['badges'],
                    words[0][1:],
                    self.shelve[self.channel].mthds
                    )
            if action:
                with self.lock:
                    res = action(sender, " ".join(words[1:]))
                    self.shelve.sync()
                return res
            else:
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

        return highlighter(True)(msg['msg'], self.emotes, twitch_indices)
