import time
from threading import Thread

class background_bot():
    def __init__(self, bot):
        self.running = False
        self.command = ""
        self.bot = bot
        self.thread = bgtask(self)

    def run(self):
        while True:
            if self.command:
                getattr(self.bot, self.command)()
                self.command = ""
            if self.running and self.bot.connection.is_connected(): self.bot.poll()
            time.sleep(0.1)

    def start(self):
        self.running = True
        self.command = "_connect"

    def stop(self):
        self.running = False
        self.command = "disconnect"

def bgtask(bgbot):
    t1 = Thread(target = bgbot.run)
    t1.start()
    return t1
