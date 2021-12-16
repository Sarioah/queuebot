import threading, shelve
from irc_bot.events import handle_event, role_check
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
        self.commands = {"testqueue"  : ("m", "test"),
                         "sr"         : ("e", "addsong"),
                         "leave"      : ("e", "leave"),
                         "openqueue"  : ("m", "open"),
                         "closequeue" : ("m", "close"),
                         "removesong" : ("m", "removesong"),
                         "removeuser" : ("m", "removeuser"),
                         "listqueue"  : ("e", "listsongs"),
                         "listusers"  : ("m", "listusers"),
                         "currentsong": ("e", "currentsong"),
                         "queue"      : ("e", "status"),
                         "picked"     : ("e", "played"),
                         "pick"       : ("m", "picksong"),}

    def handle_msg(self, chat_msg, msg_type = "pubmsg"):
        with open("messages.log", "a") as file:
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
            command = self.find_command(tags['badges'], words[0][1:])
            if not command: return
            else:
                with self.lock:
                    res = getattr(self.shelve[self.channel], command)(sender, " ".join(words[1:]))
                    self.shelve.sync()
                return res

    def find_command(self, badges, request):
        try: cmd = self.commands[request]
        except KeyError: return
        if cmd[0] == "m":
            if role_check(badges): return cmd[1]
        else: return cmd[1]
    
    def format_badges(self, msg):
        badges = msg['tags']['badges']
        res = ''
        roles = [("RED", ("broadcaster",), "B"),
                 ("GREEN", ("moderator",), "M"),
                 ("BLUE", ("subscriber", "premium"), "S"),
                 ("PURPLE", ("vip",), "V")]
        for role in roles:
            res += col(role[2], role[0]) if role_check(badges, *role[1]) else ''
        return res
