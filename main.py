import random, time
from configparser import ConfigParser
from irc_bot.background_bot import background_bot
from irc_bot.irc_bot import irc_bot
from queue.queue import Queue, trunc
from irc_bot.message_handler import message_handler

config = ConfigParser()
config.read(".config")
config = config["DEFAULT"]

q = Queue(config["channel"])
q.open()

import test
for i in test.data: q.addsong(*i)
print("Bot loaded with test queue")

m = message_handler(config["bot_prefix"], q, trunc)
bot = irc_bot(config["bot_nick"], config["tmi_token"], config["channel"], m.handle_msg)
bgbot = background_bot(bot)
bgbot.start()

def cmd(msg):
    res = m.run_cmd(msg)
    bot.send_msg(res)
    return res

while not bot.joined:
    bot.poll()
print("Bot is ready for commands")

while True:
    msg = input("> ") or '0'
    res = eval(msg)
    print(res)
    try:
        pass
    except Exception as e:
        import traceback
        print("oh no....anyway")
        traceback.print_exc()
    time.sleep(1)
