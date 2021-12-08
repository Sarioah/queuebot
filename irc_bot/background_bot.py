import time
from threading import Thread, Lock

class background_bot():
    def __init__(self, bot):
        self.running = False
        self.command = ""
        self.lock = Lock()
        self.bot = bot
        self.thread = bgtask(self)

    def run(self):
        while True:
            with self.lock:
                if self.command:
                    getattr(self.bot, self.command)()
                    self.command = ""
                if self.running and self.bot.connection.is_connected(): self.bot.poll()
            time.sleep(0.1)

    def start(self):
        with self.lock:
            self.running = True
            self.command = "_connect"

    def stop(self):
        with self.lock:
            self.running = False
            self.command = "disconnect"


    def send_command(self, command):
        while self.command:
            time.sleep(0.05)
        with self.lock:
            self.command = command
            
def bgtask(bgbot):
    t1 = Thread(target = bgbot.run)
    t1.start()
    return t1
