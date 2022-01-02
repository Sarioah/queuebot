import random, time, sys, os, colorama
from irc_bot.background_bot import background_bot
from irc_bot.irc_bot import irc_bot
from irc_bot.message_handler import message_handler
from readchar import readchar
from tools.colours import colourise as col
from tools.Queue import Queue, trunc
from tools.config import configuration, BadOAuth, check_update, password_handler as P

try: 
    import tools.version
    version = tools.version.version
except: version = "v0"

errored = False

def cmd(msg):
    res = m.run_cmd(msg)
    bot.send_msg(res)
    return res

def close(*a):
    print(col("Exiting...", "GREY"))
    try:
        bgbot.quit()
        bgbot.thread.join()
        m.shelve.close()
    except: print(col("Bot was not running", "GREY"))
    print(col("Cleanup complete", "GREY"))
    if errored:
        print("\nPress any key to exit...")
        _ = readchar()

def setup(*a):
    global m, p, bgbot, errored
    if not os.path.isdir("data"): os.mkdir("data")

    colorama.init()
    res = check_update(version)
    if res: print(res)

    try: config = configuration("config.ini").get_config()
    except Exception as e:
        print("\n" + str(e))
        errored = True
        sys.exit()

    channel = a[1].lower() if len(a) > 1 else config["channel"].lower()
    bot_name = config['bot_name'].lower()

    if os.name == "nt":
        import win32api
        win32api.SetConsoleCtrlHandler(close, True)
        win32api.SetConsoleTitle(f"Sari queuebot {version} acting as '{config['bot_name']}' in channel '{channel}'")
    p = P(bot_name)
    m = message_handler(channel, config['bot_prefix'], trunc, config['logging'])
    bot = irc_bot(bot_name, p.get_password(), channel, config['muted'], m.handle_msg, config['startup_msg'], version)
    bgbot = background_bot(bot)

    #while not bot.joined:
    #    bot.poll()
    #    time.sleep(1)
    #else: print(col("Bot is ready for commands", "GREEN"))

try:
    setup(*sys.argv)
    while True:
        if not bgbot.q.empty(): raise bgbot.q.get()
        time.sleep(1)
except (EOFError, KeyboardInterrupt, SystemExit): pass
except BadOAuth as e: 
    if str(e) == "Login authentication failed": res = "oauth token is invalid"
    elif str(e) == "Improperly formatted auth": res = "oauth token is improperly formatted"
    print(col(res + ", please restart the bot and paste in a new token", "RED"))
    p.del_password()
    errored = True
except (BaseException) as e:
    import traceback
    error = traceback.format_exc()
    print(f"{col('Bot has encounted a problem and needs to close. Error is as follows:', 'RED')}\n{error}")
    with open("last error.log", "w") as fd: fd.write(error)
    print(f"Error saved to {col('last error.log', 'YELLOW')}")
    errored = True
finally:
    if os.name != "nt" or errored: close()

