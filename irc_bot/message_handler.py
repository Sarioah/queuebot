class message_handler:
    def __init__(self, sep, q, trunc):
        self.sep = sep
        self.queue = q
        self.trunc = trunc
        self.commands = {"testqueue": "test",
                    "sr": "addsong",
                    "leave": "leave",
                    "openqueue": "open",
                    "closequeue": "close",
                    "removesong": "removesong",
                    "removeuser": "removeuser",
                    "listqueue": "listsongs",
                    "listusers": "listusers",
                    "currentsong": "currentsong",
                    "queue": "status",
                    "picked": "played",
                    "pick": "picksong"}

    def handle_msg(self, msg):
        chat_msg = msg.arguments[0]
        chat_command = chat_msg.split(" ", 1)
        chat_tags = {i["key"]: i["value"] for i in msg.tags}

        
        print("*****\n%s: %s\n******\n" % (chat_tags["display-name"], chat_msg))
        for k in chat_tags: print("%s: %s" % (k, chat_tags[k]))
        try:
            if chat_msg[:1] == self.sep:
                cmd = getattr(self.queue, self.commands[chat_command[0][1:]])
                user = chat_tags["display-name"]
                try: args = chat_command[1]
                except IndexError: args = ""
                res = cmd(user, args)
                return self.trunc(res, 450)
        except KeyError: pass