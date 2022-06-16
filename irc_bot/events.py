from datetime import datetime

from tools.chat import format_badges
from tools.text import colourise as col
from tools.config import BadOAuth


class HandleEvent:
    def __init__(self, msg):
        self.msg = msg['msg']
        self.words = msg['words']
        self.tags = msg['tags']

        prefix = f"{datetime.now():[%m-%d %H:%M:%S] }"
        self.prefix = col(prefix, "GREY")

    def __call__(self, msg_type, callback):
        try:
            action = getattr(self, "on_" + msg_type)
        except AttributeError:
            return None
        else:
            return action(callback)

    def on_pubmsg(self, callback):
        print(
            self.prefix
            + f"<{col(self.tags['display-name'], 'CYAN')}"
            + f">{format_badges(self.tags)}: "
            + f"{self.msg}"
        )
        return callback(self.msg, self.words, self.tags)

    def on_action(self, *_args):
        print(
            self.prefix
            + col(f"{self.tags['display-name']}: {self.msg}", "CYAN")
        )

    def on_pubnotice(self, *_args):
        print(
            self.prefix
            + col(self.msg, "GREY")
        )

    def on_privnotice(self, *_args):
        if self.msg in (
            "Improperly formatted auth",
            "Login authentication failed"
        ):
            raise BadOAuth(self.msg)
        print(
            self.prefix
            + col(self.msg, "GREY")
        )

    def on_usernotice(self, *_args):
        if self.tags.get("system-msg"):
            res = col(self.tags['system-msg'], "GREY")
        elif self.tags.get("display-name"):
            res = col(self.tags['display-name'], "GREY")
        print(
            self.prefix + res
            + f" - {self.msg or '<no msg>'}"
        )

    def on_whisper(self, *_args):
        print(
            self.prefix
            + col(
                f"Whisper from {self.tags['display-name']}: {self.msg}",
                "GREY"
            )
        )
