from tools.colours import colourise as col
"""
- Take the message
- Split it into relevant parts (msg body, msg as words, msg tags)
- check first word for command prefix
- process command, checking for moderator role if needed
- if command found, run associatied Queue method and return response
- failures bubble back up through to the original callback as None returns
"""
class message_handler:
    def __init__(self, sep, q, trunc):
        self.sep = sep
        self.queue = q
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

    def handle_msg(self, chat_msg):
        with open("messages.log", "a") as file:
            file.write(str(chat_msg) + "\n")

        msg = {}
        try: msg['msg'] = chat_msg.arguments[0]
        except IndexError: msg['msg'] = ""

        msg['words'] = msg['msg'].split(" ")
        msg['tags'] = {i['key']: i['value'] for i in chat_msg.tags}
        
        res = self.handle_command(**msg)
        if res: return res
        res = self.handle_systemmsg(**msg)
        if res: return res + f" - {msg['msg'] or '<no msg>'}"

        print(f"<{col(msg['tags']['display-name'], 'CYAN')}>{self.format_badges(msg)}: {msg['msg']}")
        return 

        try:
            if chat_msg[:1] == self.sep:
                cmd = getattr(self.queue, self.commands[chat_command[0][1:]][1])
                user = chat_tags["display-name"]
                try: args = chat_command[1]
                except IndexError: args = ""
                with self.queue.lock:
                    res = cmd(user, args)
                return self.trunc(res, 450)
        except KeyError: pass

    def handle_command(self, msg, words, tags):
        if words[0][:1] == self.sep:
            sender = tags['display-name']
            command = self.find_command(tags['badges'], words[0][1:])
            #command =  queue.execute, maybe pass off to new method in Queue
            return command

    def handle_systemmsg(self, msg, words, tags):
            if 'system-msg' in tags: return col(tags['system-msg'], "GREY")

    def find_command(self, badges, request):
        try: cmd = self.commands[request]
        except KeyError: return
        if cmd[0] == "m":
            if self.modcheck(badges): return cmd
        else: return cmd

    def role_check(self, badges, *roles):
        roles = roles or ("moderator", "broadcaster")
        try: return any([role in badge for badge in badges.split(",") 
                            for role in roles])
        except AttributeError: return False

    def format_badges(self, msg):
        badges = msg['tags']['badges']
        res = ''
        roles = [("RED", ("broadcaster",), "B"),
                 ("GREEN", ("moderator",), "M"),
                 ("BLUE", ("subscriber", "premium"), "S"),
                 ("PURPLE", ("vip",), "V")]
        for role in roles:
            res += col(role[2], role[0]) if self.role_check(badges, *role[1]) else ''
        return res

    def run_cmd(self, msg):
        chat_command = msg.split(" ", 1)
        try:
            if msg[:1] == self.sep:
                cmd = getattr(self.queue, self.commands[chat_command[0][1:]][1])
                user = "Sarioah"
                try: args = chat_command[1]
                except IndexError: args = ""
                with self.queue.lock:
                    res = cmd(user, args)
                return self.trunc(res, 450)
        except KeyError: pass
