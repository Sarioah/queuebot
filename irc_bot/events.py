from tools.chat import format_badges
from tools.text import colourise as col
from tools.config import BadOAuth


class handle_event():

    def __init__(self, msg):
        self.msg = msg['msg']
        self.words = msg['words']
        self.tags = msg['tags']

    def __call__(self, msg_type, callback):
        try:
            action = getattr(self, "on_" + msg_type)
        except AttributeError:
            return None
        else:
            return action(callback)

    def on_pubmsg(self, callback):
        print(
            f"<{col(self.tags['display-name'], 'CYAN')}"
            + f">{format_badges(self.tags)}: "
            + f"{self.msg}"
            )
        return callback(self.msg, self.words, self.tags)

    def on_action(self, *a):
        print(col(f"{self.tags['display-name']}: {self.msg}", "CYAN"))

    def on_pubnotice(self, *a):
        print(col(self.msg, "GREY"))

    def on_privnotice(self, *a):
        if self.msg in (
                "Improperly formatted auth",
                "Login authentication failed"):
            raise BadOAuth(self.msg)
        else:
            print(col(self.msg, "GREY"))

    def on_usernotice(self, *a):
        if 'system-msg' in self.tags:
            res = col(self.tags['system-msg'], "GREY")
            print(res + f" - {self.msg or '<no msg>'}")

    def on_whisper(self, *a):
        print(col(
            f"Whisper from {self.tags['display-name']}: {self.msg}",
            "GREY"
            ))
