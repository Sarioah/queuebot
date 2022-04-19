import os
import json

try:
    import keyring
except Exception:
    pass

from configparser import ConfigParser, ParsingError
from tools.text import colourise as col
from setuptools._vendor.packaging import version
from urllib.request import urlopen

defaults = {"bot_name": "********",
            "channel": "********",
            "bot_prefix": "!",
            "muted": "False",
            "logging": "False",
            "startup_msg": "True"}


class BadOAuth(Exception):
    pass


class password_handler():

    def __init__(self, user):
        global keyring
        self.user = user
        if os.name == "nt":
            import keyring.backends.Windows
            keyring.set_keyring(keyring.backends.Windows.WinVaultKeyring())
        else:
            import sagecipher.keyring
            keyring.set_keyring(sagecipher.keyring.Keyring())
        while not self.get_password():
            self._no_passwd()

    def _no_passwd(self):
        print(
                "Please log into twitch using your bot account, then visit "
                "%s to generate an oauth code for the bot to login with. "
                "Then paste it here and press enter.\n"
                % (col("https://twitchapps.com/tmi", "BLUE"),)
                )
        passwd = input(
                "Input your oauth code, including the 'oauth:' at the front: "
                )
        keyring.set_password("TMI", self.user, passwd)

    def get_password(self):
        return keyring.get_password("TMI", self.user)

    def del_password(self):
        return keyring.delete_password("TMI", self.user)


class configuration():

    def __init__(self, configfile):
        self.c = ConfigParser()
        self.configfile = configfile
        try:
            self.c.read(configfile)
        except ParsingError:
            self._config_bad()

        if not self.c['DEFAULT']:
            res = self._config_empty(
                "Configuration file not found, a default "
                "configuration file has been written to"
                )
        elif any([
                True for k in self.c['DEFAULT']
                if self.c['DEFAULT'][k] == "********"]):
            res = self._config_empty("Default fields need to be filled out in")
        elif any([
                True for k in ("bot_name", "channel")
                if k not in self.c['DEFAULT']]):
            res = self._config_empty("Fields missing in")
        else:
            res = ""
        self._write_config()
        if res:
            raise res

    def get_config(self):
        return self.c['DEFAULT']

    def _write_config(self):
        for k in defaults:
            if k not in self.c['DEFAULT']:
                self.c['DEFAULT'][k] = defaults[k]
        with open(self.configfile, "w") as fd:
            self.c.write(fd)

    def _config_empty(self, msg):
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
            "Send a message in chat when the bot has sucessfully connected\n"
            f"\nOnce these are filled in, restart the bot."
            )
        return Exception(res)

    def _config_bad(self):
        res = (
            f"Config file '{col(self.configfile, 'YELLOW')}' "
            "appears to be misformatted.\n Please correct the error or "
            "delete the file, then restart the bot."
            )
        return Exception("\n".join(res))


def check_update(ver):
    try:
        upstream = json.load(urlopen(
            "https://api.github.com/repos/sarioah/queuebot/releases/latest",
            timeout=3
            ))['name']
    except Exception:
        pass
    else:
        if version.parse(upstream) > version.parse(ver):
            return (
                "Updated bot found, version \"%s\".\n"
                "Please visit %s to download the new bot"
                % (
                    col(upstream, 'BLUE'),
                    col(
                        'https://github.com/Sarioah/queuebot/releases/latest',
                        'YELLOW'
                        )
                    )
                )
