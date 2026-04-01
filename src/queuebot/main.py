#!/usr/bin/python3

import os
import sys
import time
from pathlib import Path
from traceback import format_exc

import colorama
from readchar import readchar

from queuebot.irc_bot.background_bot import BackgroundBot
from queuebot.irc_bot.irc_bot import IrcBot
from queuebot.irc_bot.message_handler import MessageHandler
from queuebot.tools.config import BadOAuth, Configuration, check_update
from queuebot.tools.get_emotes import get_emotes
from queuebot.tools.song_queue import trunc
from queuebot.tools.text import colourise as col
from queuebot.tools.twitch_auth import AuthorisedContext

try:
    version_filename = os.path.join(os.path.dirname(__file__), "version.txt")
    with open(version_filename) as _fd:
        VERSION = f"v{_fd.readline().strip()}"
except OSError:
    VERSION = "v0"


class ErrorStatus:
    def __init__(self):
        self.errored = False
        self.last_error = None

    def __bool__(self):
        return self.errored

    def __str__(self):
        return self.last_error

    def set_errored(self, error):
        self.errored = True
        self.last_error = error


error_status = ErrorStatus()
bg_bot = None
message_handler = None
password_handler = None


def cmd(bot, msg):
    res_ = message_handler.handle_msg(msg)
    bot.send_command("send_msg", res_)
    return res_


def close(*_args):
    print(col("Exiting...", "GREY"))
    try:
        bg_bot.quit()
        bg_bot.thread.join()
        message_handler.song_queue.save()
    except Exception:
        print(col("Bot was not running", "GREY"))
    print(col("Cleanup complete", "GREY"))
    if error_status:
        print("\nPress any key to exit...")
        _ = readchar()


def setup_bot(*args):
    if not os.path.isdir("data"):
        os.mkdir("data")

    colorama.init()
    print(col("Checking for updates...", "GREY"))
    res_ = check_update(VERSION)
    if res_:
        print(res_)

    try:
        config = Configuration("config.ini").get_config()
    except Exception as exc_:
        print("\n" + str(exc_))
        error_status.set_errored(exc_)
        sys.exit()

    channel = args[1].casefold() if len(args) > 1 else config["channel"].casefold()
    try:
        ctx = AuthorisedContext()
    except Exception:
        print("\033[31;1mLogin failure, please restart the bot and try again\033[0m")
        print("\nPress any key to exit...")
        readchar()
        exit(1)
    bot_name = ctx.channel_name.casefold()

    print(col("Checking for FFZ/BTTV emotes...", "GREY"))
    emotes = get_emotes(channel)
    global message_handler
    message_handler = MessageHandler(
        channel, config["bot_prefix"], trunc, config["logging"], emotes
    )
    irc_bot = IrcBot(
        bot_name,
        f"oauth:{ctx.token.get('access_token')}",
        channel,
        config["muted"],
        message_handler.handle_msg,
        config["startup_msg"],
        VERSION,
    )
    global bg_bot
    bg_bot = BackgroundBot(irc_bot)


def main():
    try:
        setup_bot(*sys.argv)
        while True:
            if not bg_bot.exception_queue.empty():
                raise bg_bot.exception_queue.get()
            time.sleep(1)
    except (EOFError, KeyboardInterrupt, SystemExit):
        pass
    except BadOAuth as exc:
        if str(exc) == "Login authentication failed":
            res = "oauth token is invalid"
        elif str(exc) == "Improperly formatted auth":
            res = "oauth token is improperly formatted"
        elif str(exc) == "Login unsuccessful":
            res = "oauth token was rejected"
        else:
            res = str(exc)
        print(col(res + ", please restart the bot and log in again", "RED"))
        try:
            print("removing broken auth file")
            Path("data/login auth.json").unlink()
        except Exception as exc2:
            print(f"{exc2.__class__}: {exc2}")
        error_status.set_errored(exc)
    except Exception as exc:
        trace = format_exc()
        msg = col("Bot has encountered a problem and needs to close. Error is as follows:", "RED")
        print(f"{msg}\n{trace}")

        with open("last error.log", "w", encoding="utf-8") as file_:
            file_.write(f"Bot {VERSION}\n")
            file_.write(trace)
        print(f"Error saved to {col('last error.log', 'YELLOW')}")
        error_status.set_errored(exc)
    finally:
        if os.name != "nt" or error_status:
            close()


if __name__ == "__main__":
    main()
