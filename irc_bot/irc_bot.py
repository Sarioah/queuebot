import sys
from time import sleep
from tools.colours import colourise as col

try:
    from irc.bot import SingleServerIRCBot
except (ModuleNotFoundError, ImportError):
    print(col("IRC module not found, exiting", "RED"))
    sys.exit(1)

server = 'irc.chat.twitch.tv'
port = 6667

class irc_bot(SingleServerIRCBot):
    def __init__(self, username, password, channel, muted, message_handler):
        self.channel = '#' + channel
        self.joined = False
        self.muted = 1 if muted == "True" else 0
        self.message_handler = message_handler
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
        print(col(f"Welcomed into channel \"{self.channel[1:]}\"", "GREY"))

    def on_pubmsg(self, client, message):
        response = self.message_handler(message)
        c = "RED" if self.muted else "YELLOW"
        if not response: return
        elif not self.muted:
            client.privmsg(self.channel, response)
        print(col(f"- Bot - {response}", c))

    def on_pubnotice(self, client, message): print(f"pubnotice: {message}")
    def on_privnotice(self, client, message): print(f"privnotice: {message}")
    def on_usernotice(self, client, message): print(self.message_handler(message))
    def on_notice(self, client, message): print(f"notice: {message}")
    def on_whisper(self, client, message): print(f"whisper: {message}")
    def on_action(self, client, message): print(f"action: {message}")
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
        if self.muted: return col("Bot is muted", "RED")
        elif msg and self.joined: 
            self.client.privmsg(self.channel, msg)
            return col(f"sent {msg}", "YELLOW")
        else:
            return col("bot not ready to send", "RED")
