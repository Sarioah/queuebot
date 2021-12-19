from configparser import ConfigParser, ParsingError
from tools.colours import colourise as col

defaults = {"tmi_token" : "********",
            "bot_nick"  : "********",
            "channel"   : "********",
            "bot_prefix": "!",
            "muted"     : "False",
            "logging"   : "False"}

class configuration():
    def __init__(self, configfile):
        self.c = ConfigParser()
        self.configfile = configfile
        try:
            self.c.read(configfile)
        except ParsingError:
            self._config_bad()

        for k in defaults:
            if k not in self.c['DEFAULT']: self.c['DEFAULT'][k] = defaults[k]
        with open(self.configfile, "w") as fd:
            self.c.write(fd)

        if any([True for k in self.c['DEFAULT'] if self.c['DEFAULT'][k] == "********"]):
            self._config_empty("Default fields need to be filled out in")
        if not self.c['DEFAULT']:
            self._config_empty("Configuration file not found, a default configuration file has been written to")

    def get_config(self): return self.c['DEFAULT']

    def _config_empty(self, msg):
        res = [f"{msg} '{col(self.configfile, 'YELLOW')}'","",
               f"Please log into twitch using your bot account, then visit {col('https://twitchapps.com/tmi', 'BLUE')} to " +
               f"generate an oauth code for the bot to login with. This code needs to be entered into the config file " +
               f"('{col(self.configfile, 'YELLOW')}') along with a couple other values:","",
               f"     {col('tmi_token', 'GREEN')}  : Oauth code, including the 'oauth:' part at the front",
               f"     {col('bot_nick', 'GREEN')}   : Name of the twitch account the bot will login with",
               f"     {col('channel', 'GREEN')}    : Name of the twitch channel the bot will listen in, and send messages to",
               f"     {col('bot_prefix', 'GREEN')} : Symbol that should appear at the front of bot commands in chat. Default is '!'",
               f"     {col('muted', 'GREEN')}      : Mutes the bot if you need to stop it sending messages",
               f"     {col('logging', 'GREEN')}    : Saves each received chat message in '{col('messages.log', 'YELLOW')}', useful for debugging","",
               f"Once these are filled in, restart the bot."]
        raise Exception("\n".join(res))

    def _config_bad(self):
        res = [f"Config file '{col(self.configfile, 'YELLOW')}' appears to be misformatted.",
               f"Please correct the error or delete the file, then restart the bot."]
        raise Exception("\n".join(res))
