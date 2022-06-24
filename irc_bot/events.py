"""
Tools for handling events produced by an IRC bot

Classes:
    HandleEvent: given a message, message type and callback,
    process the message using the callback then format the response
    appropriately
"""
# TODO: Refactor, creating with the message then calling with
# the message type / callback is just silly
from datetime import datetime

from tools.chat import format_badges
from tools.text import colourise as col
from tools.config import BadOAuth


class HandleEvent:
    """
    Hold the message itself, then call with the type and callback, returning the response
    """
    def __init__(self, msg):
        """
        Create the event with the message
        """
        self.msg = msg['msg']
        self.words = msg['words']
        self.tags = msg['tags']

        prefix = f"{datetime.now():[%m-%d %H:%M:%S] }"
        self.prefix = col(prefix, "GREY")

    def __call__(self, msg_type, callback):
        """
        Call the approriate method based on the message type
        """
        try:
            action = getattr(self, "on_" + msg_type)
        except AttributeError:
            return None
        else:
            return action(callback)

    def on_pubmsg(self, callback):
        """
        Used for most user-based messages
        """
        print(
            self.prefix
            + f"<{col(self.tags['display-name'], 'CYAN')}"
            + f">{format_badges(self.tags)}: "
            + f"{self.msg}"
        )
        return callback(self.msg, self.words, self.tags)

    def on_action(self, *_args):
        """
        Used for /me actions
        """
        print(
            self.prefix
            + col(f"{self.tags['display-name']}: {self.msg}", "CYAN")
        )

    def on_pubnotice(self, *_args):
        """
        Used for user - focused system messages, including:
            - hosts, hosts going offline
            - non-fatal error messages like messages sent too fast, suspended channels
        """
        print(
            self.prefix
            + col(self.msg, "GREY")
        )

    def on_privnotice(self, *_args):
        """
        Used for fatal error messages, usually for improper client configuration
        """
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
        """
        Used for general system anouncements, including:
            - subs
            - /announcements
            - raids
        """
        if self.tags.get("system-msg"):
            res = col(self.tags['system-msg'], "GREY")
        elif self.tags.get("display-name"):
            res = col(self.tags['display-name'], "GREY")
        print(
            self.prefix + res
            + f" - {self.msg or '<no msg>'}"
        )

    def on_whisper(self, *_args):
        """
        Used for whispers
        """
        print(
            self.prefix
            + col(
                f"Whisper from {self.tags['display-name']}: {self.msg}",
                "GREY"
            )
        )
