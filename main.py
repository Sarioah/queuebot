import random, time, sys, os, colorama
from irc_bot.background_bot import background_bot
from irc_bot.irc_bot import irc_bot
from irc_bot.message_handler import message_handler
from readchar import readchar
from tools.colours import colourise as col
from tools.Queue import Queue, trunc
from tools.config import configuration

version = 'v0.9.1'

def cmd(msg):
    res = m.run_cmd(msg)
    bot.send_msg(res)
    return res

def close(*a):
    print(col("Exiting...", "GREY"))
    bgbot.quit()
    bgbot.thread.join()
    m.shelve.close()
    print(col("Cleanup complete", "GREY"))
    time.sleep(2)

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
    win32api.SetConsoleTitle(f"Sari queuebot {version} acting as '{config['bot_nick']}' in channel '{channel}'")

m = message_handler(channel, config['bot_prefix'], trunc, config['logging'])
bot = irc_bot(config['bot_nick'], config['tmi_token'], channel, config['muted'], m.handle_msg)
bgbot = background_bot(bot)

while not bot.joined: 
    bot.poll()
    time.sleep(1)
else: print(col("Bot is ready for commands", "GREEN"))

while True:
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        break
    except (BaseException) as e:
        import traceback
        error = traceback.format_exc()
        print(f"{col('Bot has encounted a problem and needs to close. Error is as follows:', 'RED')}\n{error}")
        with open("last error.log", "w") as fd: fd.write(error)
        print(f"Error saved to {col('last error.log', 'YELLOW')}")
        print(col("\nPress any key to exit...", "YELLOW"))
        _ = readchar()
        break
    time.sleep(1)

if os.name != "nt": close()

