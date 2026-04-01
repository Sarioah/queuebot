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

        if not self.config["DEFAULT"]:
            channel = input(
                "\n\033[34;1mPlease enter the channel the bot shall listen to / post in\033[0m: \033[32;1m"
            )
            print("\033[0m", end="")
            self.config["DEFAULT"]["channel"] = channel
        self.write_config()

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
