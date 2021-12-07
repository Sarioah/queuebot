import sys
import time
from configparser import ConfigParser
try:
    from irc.bot import SingleServerIRCBot
except (ModuleNotFoundError, ImportError):
    print("IRC module not found, exiting")
    sys.exit(1)

config = ConfigParser()
config.read(".config")
config = config["DEFAULT"]

server = 'irc.chat.twitch.tv'
port = 6667

class irc_bot(SingleServerIRCBot):
    def __init__(self, username, password, channel, message_handler):
        self.channel = '#' + channel
        self.message_handler = message_handler

        super().__init__([(server, port, password)], username, username)
        print('Initialising bot...')

    def on_welcome(self, client, _):
        client.cap('REQ', ':twitch.tv/membership')
        client.cap('REQ', ':twitch.tv/tags')
        client.cap('REQ', ':twitch.tv/commands')
        client.join(self.channel)
        print('welcomed')

    def on_pubmsg(self, client, message):
        response = self.message_handler(message)

        if response:
            print("Sending %s" % response)
            client.privmsg(self.channel, response)

    def on_pubnotice(self, client, message):
        print(message)

    def on_join(self, client, _):
        print('Joined channel, ready for commands!')

    def on_error():
        print('error')

    def on_disconnect():
        print('disconnect')

def start_bot(message_handler):
    channel = config["channel"]
    username = config["bot_nick"]
    password = config["tmi_token"]

    bot = irc_bot(username, password, channel, message_handler)
    print("bot starting")

    bot._connect()
    while True:
        bot.reactor.process_once(timeout = 1)
        time.sleep(3)

import random

def message_handler(msg):
    chat_message = msg.arguments[0]
    
    if chat_message == '!dice':
        return 'You rolled a {}'.format(random.randint(1, 6))
    else:
        return msg.arguments[0].split(' ')[0]

try:
    start_bot(message_handler)
except:
    print(sys.exc_info()[1])
    print('exiting')
