from tools.colours import colourise as col
from configparser import ConfigParser, ParsingError

defaults = {"TMI_TOKEN" : "********",
            "BOT_NICK"  : "********",
            "CHANNEL"   : "********",
            "BOT_PREFIX": "!",
            "MUTED"     : "False"}

class configuration():
    def __init__(self, configfile):
        self.c = ConfigParser()
        self.configfile = configfile
        try:
            self.c.read(configfile)
        except ParsingError:
            self._config_bad()

        if any([True for k in self.c['DEFAULT'] if self.c['DEFAULT'][k] == "********"]):
            self._config_empty("Default fields need to be filled out in")
        if not self.c['DEFAULT']:
            self._config_empty("Configuration file not found, a default configuration file has been written to")

    def get_config(self): return self.c['DEFAULT']

    def _config_empty(self, msg):
        for k in defaults:
            if k not in self.c['DEFAULT']: self.c['DEFAULT'][k] = defaults[k]

        with open(self.configfile, "w") as fd:
            self.c.write(fd)

        res = [f"{msg} {col(self.configfile, 'YELLOW')}","",
               f"Please log into twitch using your bot account, then visit {col('https://twitchapps.com/tmi', 'BLUE')} to generate an oauth code for the bot to login with. This code needs to be entered into the config file ({col(self.configfile, 'YELLOW')}) along with a couple other values:","",
               f"     {col('TMI_TOKEN', 'GREEN')}: Oauth code, including the 'oauth:' part at the front",
               f"     {col('BOT_NICK', 'GREEN')}: Name of the twitch account the bot will login with",
               f"     {col('CHANNEL', 'GREEN')}: Name of the twich channel the bot will listen in, and send messages to",
               f"     {col('BOT_PREFIX', 'GREEN')}: Symbol that should appear at the front of bot commands in chat.",
               f"     {col('MUTED', 'GREEN')}: Whether or not the bot is allowed to send chat messages.","",
               f"Once these are filled in, start the bot again."]
        raise Exception("\n".join(res))

    def _config_bad(self):
        res = [f"Config file '{col(self.configfile, 'YELLOW')}' appears to be misformatted.",
               f"Please correct the error or delete the file"]
        raise Exception("\n".join(res))
