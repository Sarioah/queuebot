import random, time, sys, os, colorama
from irc_bot.background_bot import background_bot
from irc_bot.irc_bot import irc_bot
from irc_bot.message_handler import message_handler
from readchar import readchar
from tools.colours import colourise as col
from tools.Queue import Queue, trunc
from tools.config import configuration, BadOAuth, password_handler as P

version = 'v1.1.0'

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

def setup(*a):
    if not os.path.isdir("data"): os.mkdir("data")

    colorama.init()

    try: config = configuration("config.ini").get_config()
    except Exception as e:
        print("\n" + str(e))
        sys.exit()

    channel = a[1] if len(a) > 1 else config["channel"]

    if os.name == "nt":
        import win32api
        win32api.SetConsoleCtrlHandler(close, True)
        win32api.SetConsoleTitle(f"Sari queuebot {version} acting as '{config['bot_nick']}' in channel '{channel}'")
    global m, p, bgbot
    p = P(channel)
    m = message_handler(channel, config['bot_prefix'], trunc, config['logging'])
    bot = irc_bot(config['bot_nick'], p.get_password(), channel, config['muted'], m.handle_msg)
    bgbot = background_bot(bot)

    #while not bot.joined:
    #    bot.poll()
    #    time.sleep(1)
    #else: print(col("Bot is ready for commands", "GREEN"))

try:
    setup(sys.argv)
    while True:
        if not bgbot.q.empty(): raise bgbot.q.get()
        time.sleep(1)
except (EOFError, KeyboardInterrupt, SystemExit): pass
except BadOAuth as e: 
    if str(e) == "Login authentication failed": res = "oauth token is invalid"
    elif str(e) == "Improperly formatted auth": res = "oauth token is improperly formatted"
    print(col(res + ", please restart the bot and paste in a new token", "RED"))
    p.del_password()
except (BaseException) as e:
    import traceback
    error = traceback.format_exc()
    print(f"{col('Bot has encounted a problem and needs to close. Error is as follows:', 'RED')}\n{error}")
    with open("last error.log", "w") as fd: fd.write(error)
    print(f"Error saved to {col('last error.log', 'YELLOW')}")
finally:
    print("\nPress any key to exit...")
    _ = readchar()
    if os.name != "nt": close()

