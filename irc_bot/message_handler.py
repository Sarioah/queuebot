import threading, shelve
from irc_bot.events import handle_event
from tools.chat import role_check, CommandHandler
from tools.text import colourise as col
from tools.Queue import Queue

class message_handler:
    def __init__(self, channel, sep, trunc, logging):
        self.sep = sep
        self.channel = channel
        self.commandhandler = CommandHandler()
        self.shelve = shelve.open(f"data/{self.channel}.db", "c", writeback = True)
        if self.channel not in self.shelve:
            self.shelve[self.channel] = Queue(self.channel)
        self.lock = threading.Lock()
        self.logging = True if logging == "True" else False
        self.trunc = trunc

    def handle_msg(self, chat_msg, msg_type = "pubmsg"):
        if self.logging:
            with open("messages.log", "a", encoding = "UTF-8") as file:
                file.write(str(chat_msg) + "\n")

        msg = {}
        try: msg['msg'] = chat_msg.arguments[0]
        except IndexError: msg['msg'] = ""

        msg['words'] = msg['msg'].split(" ")
        msg['tags'] = {i['key']: i['value'] for i in chat_msg.tags}
       
        return handle_event(msg)(msg_type, self.handle_command)

    def handle_command(self, msg, words, tags):
        if words[0][:1] == self.sep:
            sender = tags['display-name']
            action = self.commandhandler.find_command(tags['badges'],
                                                      words[0][1:],
                                                      self.shelve[self.channel].mthds)
            if action:
                with self.lock:
                    res = action(sender, " ".join(words[1:]))
                    self.shelve.sync()
                return res
