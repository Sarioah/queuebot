"""Provide classes to run a chatbot in a background thread.

This might be preferable to running the bot directly in the case where
the program wants to use the foreground thread for other tasks.

Classes:
    BackgroundBot: The bot itself.

Functions:
    background_task: Start a bot thread, then return the thread handle.
"""

import time

from threading import Thread, Lock
from queue import Queue
from tools.text import colourise as col


class BackgroundBot:
    """Create a bot that runs in the background.

    Contains:
        - an IRC chatbot
        - a lock to use when writing commands for the IRC chatbot to execute
        - an exception queue to pass critical / unhandled exceptions
          back out to the main program, in a thread-safe manner
    """

    def __init__(self, bot):
        """Create the bot and retain information about the bot's operation.

        Args:
            bot: Expects an IRC bot implementing .poll, .reconnect etc.
        """
        self.running = True
        self.connect_delay = 1
        self.command = []
        self.lock = Lock()
        self.bot = bot
        self.exception_queue = Queue()
        self.thread = background_task(self)

    def run(self, exception_queue):
        """Monitor the bot's state, passing it commands to execute.

        Catch exceptions if they reach this level, passing them back
        out through the exception queue.

        Args:
            exception_queue: Threadsafe Queue object to pass Exceptions into,
                for further processing 'upstream'.
        """

        def _do_work():
            while True:
                with self.lock:
                    if self.bot.connected():
                        self.bot.poll()
                    else:
                        self.reconnect()

                    if self.command:
                        getattr(self.bot, self.command[0])(*self.command[1])
                        self.command = []
                    elif not self.running:
                        break
                time.sleep(0.1)
            print("\nBot stopped")

        try:
            _do_work()
        except Exception as exc:
            exception_queue.put(exc)

    def mute(self):
        """Mute the inner bot."""
        self.bot.muted = True

    def unmute(self):
        """Unmute the inner bot."""
        self.bot.muted = False

    def start(self):
        """Start the inner bot."""
        self.send_command("_connect")

    def stop(self):
        """Stop the inner bot."""
        self.send_command("disconnect")

    def quit(self):
        """Destroy the inner bot."""
        with self.lock:
            self.running = False
        self.send_command("die")

    def reconnect(self):
        """Attempt to reconnect the inner bot to its server.

        Wait progressively longer between reconnection attempts
        to avoid the bot spamming its server in the event a fault takes
        a long time to resolve.
        """
        while not self.bot.connected():
            print(col("Bot is attempting reconnection...", "GREY"))
            time.sleep(self.connect_delay)
            self.bot.start_bot()
            self.connect_delay *= 2
        self.connect_delay = 1

    def say(self, msg):
        """Send a msg through the inner bot to its server."""
        self.send_command("send_msg", msg)

    def send_command(self, command, *args):
        """Send an arbitrary command through to the inner bot.

        Args:
            command: Command string to send.
            args: Parameters given to the command.
        """
        while self.command:
            time.sleep(0.05)
        with self.lock:
            self.command += [command, args]


def background_task(background_bot):
    """Create a BackgroundBot on a different thread.

    Args:
        background_bot: Bot object to run in the other thread.

    Returns:
        bot_thread: Handle of the new thread to control the bot with.
    """
    bot_thread = Thread(
        target=background_bot.run, args=(background_bot.exception_queue,)
    )
    bot_thread.start()
    return bot_thread
