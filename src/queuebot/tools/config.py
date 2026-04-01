"""Tools to handle configuration of the bot.

Includes classes for password and configuration objects that work across unix
or Windows systems.

Classes:
    Configuration: Handle loading config data from a file.
    PasswordHandler: Handle loading and storing passwords.

Functions:
    check_update: Check for newer versions of the bot on GitHub.

Exceptions:
    BadOAuth: Raised when an OAuth token is rejected.
"""

import contextlib
import json
from configparser import ConfigParser, ParsingError
from urllib.request import urlopen

from packaging.version import parse

from .text import colourise as col

DEFAULTS = {
    "bot_name": "********",
    "channel": "********",
    "bot_prefix": "!",
    "muted": "False",
    "logging": "False",
    "startup_msg": "True",
}


class BadOAuth(Exception):
    """Raise exception when a server rejects an oauth token."""


class Configuration:
    """Contain methods for handling configuration data."""

    def __init__(self, configfile):
        """Create a configuration object.

        Args:
            configfile: Name of the configuration file to load data from.

        Raises:
            _config_bad: If the config file could not be read correctly.
            res: Exception for other issues with the content of the config
                file. May be raised if a default field is found, or a required
                field is missing.
        """
        self.config = ConfigParser()
        self.configfile = configfile
        try:
            self.config.read(configfile)
        except ParsingError as exc:
            raise self._config_bad() from exc
        # TODO: Giant if-elif and convoluted timing of raising / writing
        # TODO: needs revising
        if not self.config["DEFAULT"]:
            res = self._config_empty(
                "Configuration file not found, a default configuration file has been written to"
            )
        elif any(True for k in self.config["DEFAULT"] if self.config["DEFAULT"][k] == "********"):
            res = self._config_empty("Default fields need to be filled out in")
        elif any(True for k in ("bot_name", "channel") if k not in self.config["DEFAULT"]):
            res = self._config_empty("Fields missing in")
        else:
            res = ""
        self.write_config()
        if res:
            raise res

    def get_config(self):
        """Retrieve the dict containing the loaded configuration data."""
        return self.config["DEFAULT"]

    def write_config(self):
        """Write configuration data to self's configfile."""
        for key, value in DEFAULTS.items():
            if key not in self.config["DEFAULT"]:
                self.config["DEFAULT"][key] = value
        with open(self.configfile, "w", encoding="utf-8") as file_:
            self.config.write(file_)

    def _config_empty(self, msg):
        """Return an exception if fields missing from the config file.

        Args:
            msg: Description of the problem to pass through to the Exception.

        Returns:
            Exception describing the issue, as well as a short description of
            the config file's fields.
        """
        res = (
            f"{msg} '{col(self.configfile, 'YELLOW')}'.\n"
            "Please open this file and fill out the relevant fields:\n"
            f"     {col('bot_name', 'GREEN')}    : "
            "Name of the twitch account the bot will login with\n"
            f"     {col('channel', 'GREEN')}     : "
            "Name of the twitch channel the bot will listen "
            "in, and send messages to\n"
            f"     {col('bot_prefix', 'GREEN')}  : "
            "Symbol that should appear at the front of "
            "bot commands in chat. Default is '!'\n"
            f"     {col('muted', 'GREEN')}       : "
            "Mutes the bot if you need to stop it sending messages\n"
            f"     {col('logging', 'GREEN')}     : "
            "Saves each received chat message in "
            f"'{col('messages.log', 'YELLOW')}', useful for debugging\n"
            f"     {col('startup_msg', 'GREEN')} : "
            "Send a message in chat when the bot has successfully connected\n"
            f"\nOnce these are filled in, restart the bot."
        )
        return Exception(res)

    def _config_bad(self):
        """Return an exception if config file could not be properly loaded."""
        res = (
            f"Config file '{col(self.configfile, 'YELLOW')}' "
            "appears to be mis-formatted.\nPlease correct the error or "
            "delete the file, then restart the bot.\n"
        )
        return Exception(res)


def check_update(ver):
    """Check for an updated version of the program.

    Silently ignore any errors allowing the program to move on.

    Args:
        ver (str): Current bot version.

    Returns:
        Empty string, or string with info about a newer bot version.
    """
    with contextlib.suppress(Exception):
        with urlopen(
            "https://api.github.com/repos/sarioah/queuebot/releases/latest", timeout=3
        ) as url:
            upstream = json.load(url)["name"]
        if parse(upstream) > parse(ver):
            version_coloured = col(upstream, "BLUE")
            link = col("https://github.com/Sarioah/queuebot/releases/latest", "YELLOW")
            return (
                f'Updated bot found, version "{version_coloured}".\n'
                f"Please visit {link} to download the new bot"
            )
    return None
