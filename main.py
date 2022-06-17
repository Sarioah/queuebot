#!/usr/bin/python3

import time
import sys
import os

import colorama

from irc_bot.background_bot import BackgroundBot
from irc_bot.irc_bot import IrcBot
from irc_bot.message_handler import MessageHandler
from readchar import readchar

from tools.text import colourise as col
from tools.song_queue import trunc
from tools.config import Configuration, BadOAuth, check_update
from tools.config import PasswordHandler
from tools.get_emotes import get_emotes

try:
    import tools.version
    version = tools.version.version
except Exception:
    version = "v0"

errored = False


def cmd(msg):
    res = message_handler.run_cmd(msg)
    bgbot.send_msg(res)
    return res


def close(*a):
    print(col("Exiting...", "GREY"))
    try:
        bgbot.quit()
        bgbot.thread.join()
        message_handler.song_queue.save()
    except Exception:
        print(col("Bot was not running", "GREY"))
    print(col("Cleanup complete", "GREY"))
    if errored:
        print("\nPress any key to exit...")
        _ = readchar()


def setup(*a):
    global message_handler, password_handler, bgbot, errored
    if not os.path.isdir("data"):
        os.mkdir("data")

    colorama.init()
    print(col("Checking for updates...", "GREY"))
    res = check_update(version)
    if res:
        print(res)

    try:
        config = Configuration("config.ini").get_config()
    except Exception as e:
        print("\n" + str(e))
        errored = True
        sys.exit()

    channel = a[1].lower() if len(a) > 1 else config["channel"].lower()
    bot_name = config['bot_name'].lower()

    if os.name == "nt":
        import win32api
        win32api.SetConsoleCtrlHandler(close, True)
        win32api.SetConsoleTitle(
                f"Sari queuebot {version} acting as "
                + f"'{config['bot_name']}' in channel '{channel}'"
                )
    password_handler = PasswordHandler(bot_name)
    print(col("Checking for FFZ/BTTV emotes...", "GREY"))
    emotes = get_emotes(channel)
    message_handler = MessageHandler(
            channel, config['bot_prefix'],
            trunc, config['logging'], emotes
            )
    bot = IrcBot(
            bot_name, password_handler.get_password(), channel,
            config['muted'], message_handler.handle_msg,
            config['startup_msg'], version
            )
    bgbot = BackgroundBot(bot)

    # while not bot.joined:
    #     bot.poll()
    #     time.sleep(1)
    # else: print(col("Bot is ready for commands", "GREEN"))


try:
    setup(*sys.argv)
    while True:
        if not bgbot.exception_queue.empty():
            raise bgbot.exception_queue.get()
        time.sleep(1)
except (EOFError, KeyboardInterrupt, SystemExit):
    pass
except BadOAuth as e:
    if str(e) == "Login authentication failed":
        res = "oauth token is invalid"
    elif str(e) == "Improperly formatted auth":
        res = "oauth token is improperly formatted"
    print(col(
        res + ", please restart the bot and paste in a new token", "RED"
        ))
    password_handler.del_password()
    errored = True
except BaseException:
    import traceback
    error = traceback.format_exc()
    print(
        "%s\n%s"
        % (
            col(
                "Bot has encounted a problem and needs to close. "
                "Error is as follows:",
                "RED"
                ),
            error
            )
        )
    with open("last error.log", "w") as fd:
        fd.write(f"Bot {version}\n")
        fd.write(error)
    print(f"Error saved to {col('last error.log', 'YELLOW')}")
    errored = True
finally:
    if os.name != "nt" or errored:
        close()
