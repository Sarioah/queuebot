"""Tools for handling events produced by an IRC bot.

Classes:
    HandleEvent: Given a message, message type and callback,
        process the message using the callback then format the response
        appropriately.
"""

# TODO: Refactor, creating with the message then calling with
# TODO: the message type / callback is just silly
from datetime import datetime

from tools.chat import format_badges
from tools.config import BadOAuth
from tools.text import colourise as col


class HandleEvent:
    """Process an IRC event.

    Hold the message itself, then call with the type and callback, returning
    the response.
    """

    def __init__(self, msg):
        """Create the event with the message.

        Args:
            msg: Msg object received from IRC.
        """
        self.msg = msg["msg"]
        self.words = msg["words"]
        self.tags = msg["tags"]

        prefix = f"{datetime.now():[%m-%d %H:%M:%S] }"
        self.prefix = col(prefix, "GREY")

    def __call__(self, msg_type, callback):
        """Call the appropriate method based on the message type.

        Args:
            msg_type: String representing the type of message this is, and thus
                what type of handler to invoke.
            callback: Function that should be called once the response message
                has been formatted. Msg_types that only print to console don't
                typically use this.

        Returns:
            action: method used to process and respond to the message
        """
        try:
            action = getattr(self, "on_" + msg_type)
        except AttributeError:
            return None
        else:
            return action(callback)

    def on_pubmsg(self, callback):
        """Process most user-based messages.

        Args:
            callback: Function used to process the formatted message.

        Returns:
            Result of the callback function
        """
        print(
            self.prefix
            + f"<{col(self.tags['display-name'], 'CYAN')}"
            + f">{format_badges(self.tags)}: "
            + f"{self.msg}"
        )
        return callback(self.msg, self.words, self.tags)

    def on_action(self, *_args):
        """Process /me actions."""
        print(self.prefix + col(f"{self.tags['display-name']}: {self.msg}", "CYAN"))

    def on_pubnotice(self, *_args):
        """Process user - focused system messages.

        On Twitch this includes:
            - hosts, hosts going offline
            - non-fatal error messages like messages sent too fast, suspended
              channels

        Args:
            _args: Ignore extra positional args.
        """
        print(self.prefix + col(self.msg, "GREY"))

    def on_privnotice(self, *_args):
        """Process fatal error messages.

        Usually sent in response to improper client configuration.

        Args:
            _args: Ignore extra positional args.

        Raises:
            BadOAuth: Raise exception if the server rejects our configuration.
        """
        if self.msg in (
            "Improperly formatted auth",
            "Login authentication failed",
        ):
            raise BadOAuth(self.msg)
        print(self.prefix + col(self.msg, "GREY"))

    def on_usernotice(self, *_args):
        """Process general system announcements.

        On Twitch this includes:
            - subs
            - /announcements
            - raids

        Args:
            _args: Ignore extra positional args.
        """
        if tag := self.tags.get("system-msg"):
            col_tag = col(tag, "GREY")
        elif tag := self.tags.get("display-name"):
            col_tag = col(tag, "GREY")
        else:
            col_tag = col("unknown msg type", "GREY")
        print(f"{self.prefix}{col_tag} - {self.msg or '<no msg>'}")

    def on_whisper(self, *_args):
        """Process whispers.

        Args:
            _args: Ignore extra positional args.
        """
        print(
            self.prefix
            + col(f"Whisper from {self.tags['display-name']}: {self.msg}", "GREY")
        )
