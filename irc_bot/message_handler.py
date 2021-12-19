import threading, shelve, time
from irc_bot.events import handle_event
from tools.chat import role_check
from tools.colours import colourise as col
from tools.Queue import Queue
"""
- Take the message
- Split it into relevant parts (msg body, msg as words, msg tags)
- check first word for command prefix
- process command, checking for moderator role if needed
- if command found, run associated Queue method and return response
- failures bubble back up through to the original callback as None returns
"""
class message_handler:
    def __init__(self, channel, sep, trunc):
        self.sep = sep
        self.channel = channel
        self.shelve = shelve.open(f"data/{self.channel}.db", "c", writeback = True)
        if self.channel not in self.shelve:
            self.shelve[self.channel] = Queue(self.channel)
        self.lock = threading.Lock()
        self.trunc = trunc
        self.commands = {"sr"         : ("e", "addsong",      0),
                         "leave"      : ("e", "leave",        0),
                         "openqueue"  : ("m", "open",         3),
                         "closequeue" : ("m", "close",        3),
                         "clearqueue" : ("m", "clear",        3),
                         "removesong" : ("m", "removesong",   3),
                         "removeuser" : ("m", "removeuser",   3),
                         "listqueue"  : ("e", "listsongs",   10),
                         "listusers"  : ("m", "listusers",   15),
                         "currentsong": ("e", "currentsong", 10),
                         "queue"      : ("e", "status",       0),
                         "picked"     : ("e", "played",      10),
                         "pick"       : ("m", "picksong",     3),}
        self.cooldowns = {k: 0 for k in self.commands}

    def handle_msg(self, chat_msg, msg_type = "pubmsg"):
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
            command = words[0][1:].lower()
            action = self.find_command(tags['badges'], command)
            if not action: return
            else:
                if not self.check_cooldown(command): return
                with self.lock:
                    res = getattr(self.shelve[self.channel], action)(sender, " ".join(words[1:]))
                    self.shelve.sync()
                return res

    def check_cooldown(self, cmd):
        current = time.clock_gettime(0)
        timeleft = current - self.cooldowns.get(cmd, 0) - self.commands[cmd][2]
        if timeleft >= 0:
            self.cooldowns[cmd] = current
            return True
        else:
            print(col(f"'{cmd}' still on cooldown for {round(timeleft, 1) * -1}s", "GREY"))

    def find_command(self, badges, request):
        try: cmd = self.commands[request]
        except KeyError: return
        if cmd[0] == "m":
            if role_check(badges): return cmd[1]
        else: return cmd[1]
