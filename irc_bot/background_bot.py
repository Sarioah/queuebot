import time

from threading import Thread, Lock
from queue import Queue as Q
from tools.text import colourise as col


class BackgroundBot:
    def __init__(self, bot):
        self.running = True
        self.connect_delay = 1
        self.command = []
        self.lock = Lock()
        self.bot = bot
        self.exception_queue = Q()
        self.thread = bgtask(self)

    def run(self, exception_queue):
        def do_work():
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
            do_work()
        except Exception as exc:
            exception_queue.put(exc)

    def mute(self):
        self.bot.muted = True

    def unmute(self):
        self.bot.muted = False

    def start(self):
        self.send_command("_connect")

    def stop(self):
        self.send_command("disconnect")

    def quit(self):
        with self.lock:
            self.running = False
        self.send_command("die")

    def reconnect(self):
        while not self.bot.connected():
            print(col("Bot is attempting reconnection...", "GREY"))
            time.sleep(self.connect_delay)
            self.bot.start_bot()
            self.connect_delay *= 2
        self.connect_delay = 1

    def say(self, msg):
        self.send_command("send_msg", msg)

    def send_command(self, command, *args):
        while self.command:
            time.sleep(0.05)
        with self.lock:
            self.command += [command, args]


def bgtask(bgbot):
    bot_thread = Thread(target=bgbot.run, args=(bgbot.exception_queue,))
    bot_thread.start()
    return bot_thread
