from tools.chat import format_badges
from tools.colours import colourise as col

class handle_event():
    def __init__(self, msg):
        self.msg = msg['msg']
        self.words = msg['words']
        self.tags = msg['tags']

    def __call__(self, msg_type, callback):
        try: action = getattr(self, "on_" + msg_type)
        except AttributeError: return
        return action(callback)

    def on_pubmsg(self, callback):
        print(f"<{col(self.tags['display-name'], 'CYAN')}>{format_badges(self.tags)}: {self.msg}")
        return callback(self.msg, self.words, self.tags)
    def on_action(self, *a): print(col(f"{self.tags['display-name']}: {self.msg}", "CYAN"))
    def on_pubnotice(self, *a): print(col(self.msg, "GREY"))
    def on_privnotice(self, *a): print(col(self.msg, "GREY"))
    def on_usernotice(self, *a):
        res = col(self.tags['system-msg'], "GREY" ) if 'system-msg' in self.tags else ''
        if res: print(res + f" - {self.msg or '<no msg>'}")
    def on_whisper(self, *a):
        print(col(f"Whisper from {self.tags['display-name']}: {self.msg}", "GREY"))
