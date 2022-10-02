"""
Wraps / reimplements an IRC client
"""
from irc.bot import SingleServerIRCBot

from tools.text import colourise as col
from tools.text import trim_bytes


SERVER = "irc.chat.twitch.tv"
PORT = 6667
MSG_LIMIT = 499


class IrcBot(SingleServerIRCBot):
    """
    IRC Client, accepts a MessageHandler that processes messages and
    generates appropriate responses where necessary
    """

    def __init__(self, username, password, channel, muted, message_handler, startup_msg, version):
        """Create the bot. Password should be an 'oauth' token if using with Twitch' IRC api"""
        self.channel = "#" + channel
        self.client = None
        self.joined = False
        self.muted = bool(muted.lower() == "true")
        self.startup_msg = bool(startup_msg.lower() == "true")
        self.message_handler = message_handler
        self.message_limit = MSG_LIMIT - len(channel)
        self.version = version

        super().__init__(
            server_list=[(SERVER, PORT, password)],
            nickname=username,
            realname=username,
        )
        print(col("Initialising bot...", "GREY"))
        if self.muted:
            print(col("Bot is muted", "RED"))

    def on_welcome(self, client, _msg):
        """Respond to a channel's welcome message with the client's capabilities"""
        client.cap("REQ", ":twitch.tv/membership")
        client.cap("REQ", ":twitch.tv/tags")
        client.cap("REQ", ":twitch.tv/commands")
        client.join(self.channel)

        self.client = client
        self.joined = True
        print(col(f'Welcomed into channel "{self.channel[1:]}"', "GREEN"))
        if self.startup_msg:
            self.send_msg(f"Queuebot {self.version} started")

    def on_pubmsg(self, _client, msg):
        """Respond to messages posted in the channel"""
        self.send_msg(self.message_handler(msg, "pubmsg"))

    def on_pubnotice(self, _client, msg):
        """Respond to pubnotices in the channel"""
        self.message_handler(msg, "pubnotice")

    def on_privnotice(self, _client, msg):
        """Respond to privnotices in the channel"""
        self.message_handler(msg, "privnotice")

    def on_usernotice(self, _client, msg):
        """Respond to usernotices in the channel"""
        self.message_handler(msg, "usernotice")

    def on_whisper(self, _client, msg):
        """Respond to whispers to the user"""
        self.message_handler(msg, "whisper")

    def on_action(self, _client, msg):
        """Respond to actions posted in the channel"""
        self.message_handler(msg, "action")

    def on_join(self, _client, _msg):
        """Additional behaviour called when joining the channel"""

    def on_leave(self, _client, _msg):
        """Additional behaviour called when parting from a channel"""

    def on_error(self, _client, _msg):
        """Handle error sent from the server"""
        print(col("Error", "RED"))

    def on_disconnect(self, _client, _msg):
        """Additional behaviour called on server disconnect"""
        self.joined = False
        print(col("Disconnect...", "RED"))

    def connected(self):
        """Return whether the bot is connected to its server"""
        return self.connection.is_connected()

    def start_bot(self):
        """Connect the bot to its server"""
        print(col("Bot starting...", "GREY"))
        self._connect()

    def poll(self):
        """Handle any events the reactor has queued up since the last poll"""
        self.reactor.process_once()

    def send_msg(self, msg):
        """Post a message to the connected channel"""
        msg, _ = trim_bytes(msg, self.message_limit)
        if msg:
            colour = "RED" if self.muted else "YELLOW"
            print(col(msg, colour))
            if self.joined and not self.muted:
                self.client.privmsg(self.channel, msg)
