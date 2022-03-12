import sys
from time import sleep
from tools.text import colourise as col
from tools.text import trim_bytes

try:
    from irc.bot import SingleServerIRCBot
except (ModuleNotFoundError, ImportError):
    print(col("IRC module not found, exiting", "RED"))
    sys.exit(1)

server = 'irc.chat.twitch.tv'
port = 6667
msg_limit = 499

class irc_bot(SingleServerIRCBot):
    def __init__(self, username, password, channel, muted, message_handler, startup_msg, version):
        self.channel = '#' + channel
        self.joined = False
        self.muted = True if muted.lower() == "true" else False
        self.startup_msg = True if startup_msg.lower() == "true" else False
        self.message_handler = message_handler
        self.message_limit = msg_limit - len(channel)
        self.version = version
        super().__init__([(server, port, password)], username, username)

        print(col("Initialising bot...", "GREY"))
        if self.muted: print(col("Bot is muted", "RED"))

    def on_welcome(self, client, _):
        client.cap('REQ', ':twitch.tv/membership')
        client.cap('REQ', ':twitch.tv/tags')
        client.cap('REQ', ':twitch.tv/commands')
        client.join(self.channel)

        self.client = client
        self.joined = True
        print(col(f"Welcomed into channel \"{self.channel[1:]}\"", "GREEN"))
        if self.startup_msg: self.send_msg(f"Queuebot {self.version} started")

    def on_pubmsg(self, client, message):
        response, _ = trim_bytes(self.message_handler(message, "pubmsg"), self.message_limit)
        if response:
            c = "RED" if self.muted else "YELLOW"
            print(col(response, c))
            if not self.muted:
                client.privmsg(self.channel, response)

    def on_pubnotice(self, client, message): self.message_handler(message, "pubnotice")
    def on_privnotice(self, client, message): self.message_handler(message, "privnotice")
    def on_usernotice(self, client, message): self.message_handler(message, "usernotice")
    def on_whisper(self, client, message): self.message_handler(message, "whisper") 
    def on_action(self, client, message): self.message_handler(message, "action")
    def on_join(self, client, _): pass
    def on_leave(self, client, _): pass
    def on_error(self, client, _): print(col("Error", "RED"))
    def on_disconnect(self, client, _): 
        self.joined = False
        print(col("Disconnect...", "RED"))

    def connected(self): return self.connection.is_connected()

    def start_bot(self):
        print(col("Bot starting...", "GREY"))
        self._connect()

    def poll(self): self.reactor.process_once()

    def send_msg(self, msg):
        msg, _ = trim_bytes(msg, self.message_limit)
        colour = "RED" if self.muted else "YELLOW"
        if msg and self.joined and not self.muted: self.client.privmsg(self.channel, msg)
        print(col(msg, colour))
