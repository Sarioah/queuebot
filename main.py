import random, time, sys, os, colorama
from irc_bot.background_bot import background_bot
from irc_bot.irc_bot import irc_bot
from irc_bot.message_handler import message_handler
from readchar import readchar
from tools.colours import colourise as col
from tools.Queue import Queue, trunc
from tools.config import configuration

def cmd(msg):
    res = m.run_cmd(msg)
    bot.send_msg(res)
    return res

def close(*a):
    print("Exiting...")
    bgbot.quit()
    bgbot.thread.join()
    m.shelve.close()
    print("Cleanup complete")
    time.sleep(3)

if not os.path.isdir("data"): os.mkdir("data")

colorama.init()

try: config = configuration(".config").get_config()
except Exception as e: 
    print(str(e) + col('\nPress any key to exit...', "GREY"))
    _ = readchar()
    sys.exit()

channel = sys.argv[1] if len(sys.argv) > 1 else config["channel"]

if os.name == "nt":
    import win32api
    win32api.SetConsoleCtrlHandler(close, True)
    win32api.SetConsoleTitle(f"Sari queuebot acting as '{config['bot_nick']}' in channel '{channel}'")

m = message_handler(channel, config["bot_prefix"], trunc)
bot = irc_bot(config["bot_nick"], config["tmi_token"], channel, config["muted"], m.handle_msg)
bgbot = background_bot(bot)

while not bot.joined: 
    bot.poll()
    time.sleep(1)
else: print(col("Bot is ready for commands", "GREEN"))

while True:
    try:
        msg = input("> ") or '0'
        res = eval(msg)
        print(res)
    except (KeyboardInterrupt, EOFError):
        break
    except Exception as e:
        import traceback
        print("oh no....anyway")
        traceback.print_exc()
    time.sleep(1)

if os.name != "nt": close()

