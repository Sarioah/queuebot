from time import sleep

try:
    from irc.bot import SingleServerIRCBot
except (ModuleNotFoundError, ImportError):
    print("IRC module not found, exiting")
    sys.exit(1)

server = 'irc.chat.twitch.tv'
port = 6667

class irc_bot(SingleServerIRCBot):
    def __init__(self, username, password, channel, message_handler):
        self.channel = '#' + channel
        self.joined = False
        self.message_handler = message_handler

        super().__init__([(server, port, password)], username, username)
        print('Initialising bot...')

    def on_welcome(self, client, _):
        client.cap('REQ', ':twitch.tv/membership')
        client.cap('REQ', ':twitch.tv/tags')
        client.cap('REQ', ':twitch.tv/commands')
        client.join(self.channel)

        self.client = client
        self.joined = True
        print("Welcomed into channel \"%s\"" % self.channel[1:])

    def on_pubmsg(self, client, message):
        response = self.message_handler(message)

        if response: 
            print("- Bot - %s" % response)
            client.privmsg(self.channel, response)

    def on_pubnotice(self, client, message): print(message)
    def on_join(self, client, _): pass
    def on_leave(self, client, _): pass
    def on_error(self, client, _): print('error')
    def on_disconnect(self, client, _): 
        print('disconnect')

    def start_bot(self):
        print("Bot starting...")
        self._connect()

    def poll(self): self.reactor.process_once()

    def send_msg(self, msg): 
        if self.joined: 
            self.client.privmsg(self.channel, msg)
            return "sent %s" % msg
        else:
            return "bot not ready to send"
