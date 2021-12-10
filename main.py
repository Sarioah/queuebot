import random, time, sys
from configparser import ConfigParser
from irc_bot.background_bot import background_bot
from irc_bot.irc_bot import irc_bot
from irc_bot.message_handler import message_handler
from tools.colours import colourise as col
from queue.queue import Queue, trunc

config = ConfigParser()
config.read(".config")
config = config["DEFAULT"]

q = Queue(config["channel"])
q.open()

#import test
#for i in test.data: q.addsong(*i)
#print("Bot loaded with test queue")

m = message_handler(config["bot_prefix"], q, trunc)
channel = sys.argv[1] if len(sys.argv) > 1 else config["channel"]
bot = irc_bot(config["bot_nick"], config["tmi_token"], channel, config["muted"], m.handle_msg)
bgbot = background_bot(bot)

def cmd(msg):
    res = m.run_cmd(msg)
    bot.send_msg(res)
    return res

while not bot.joined: bot.poll()
else: print(col("Bot is ready for commands", "GREEN"))

while True:
    try:
        msg = input("> ") or '0'
        res = eval(msg)
        print(res)
    except KeyboardInterrupt:
        bgbot.quit()
        break
    except Exception as e:
        import traceback
        print("oh no....anyway")
        traceback.print_exc()
    time.sleep(1)

print("Exiting...")
