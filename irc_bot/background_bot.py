import time
from threading import Thread, Lock
from queue import Queue as Q
from tools.colours import colourise as col

class background_bot():
    def __init__(self, bot):
        self.running = True
        self.connect_delay = 1
        self.command = []
        self.lock = Lock()
        self.bot = bot
        self.q = Q()
        self.thread = bgtask(self)

    def run(self, q):
        def do_work():
            while True:
                with self.lock:
                    if self.bot.connected(): self.bot.poll()
                    else: self.reconnect()

                    if self.command:
                        getattr(self.bot, self.command[0])(*self.command[1])
                        self.command = []
                    elif not self.running: break
                time.sleep(0.1)
            print("\nBot stopped")

        try: do_work()
        except Exception as e: q.put(e)

    def mute(self):   self.bot.muted = True
    def unmute(self): self.bot.muted = False
    def start(self):  self.send_command("_connect")
    def stop(self):   self.send_command("disconnect")
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
        else: self.connect_delay = 1

    def say(self, msg): self.send_command("send_msg", msg)

    def send_command(self, command, *a):
        while self.command:
            time.sleep(0.05)
        with self.lock:
            self.command += [command, a]
            
def bgtask(bgbot):
    t1 = Thread(target = bgbot.run, args = (bgbot.q,))
    t1.start()
    return t1
