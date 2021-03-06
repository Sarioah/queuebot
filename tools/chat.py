import time

from tools.text import colourise as col


class CommandFound(Exception):
    """Signals that a command was found"""
    pass


class Commands():
    """Object holding generic commands that aren't bound methods elsewhere"""

    def __init__(self, parent):
        """Creates a Commands object"""
        self.parent = parent

    def help(self, *a):
        """Lists available chat commands"""
        everyone = [
                k for k in self.parent.commands
                if self.parent.commands[k][0] == "e"
                ]
        mods = [
                k for k in self.parent.commands
                if self.parent.commands[k][0] == "m"
                ]
        return (
                f"Queuebot commands: \"{', '.join(everyone)}\" "
                + f"• Queuebot moderator commands: \"{', '.join(mods)}\""
                )


class CommandHandler():

    def __init__(self):
        """Creates a CommandHandler object"""
        self.mthds = Commands(self)
        self.commands = {
                "sr"           : ("e", "addentry",      0),
                "leave"        : ("e", "leave",         0),
                "openqueue"    : ("m", "open",          3),
                "closequeue"   : ("m", "close",         3),
                "clearqueue"   : ("m", "clear",         3),
                "removesong"   : ("m", "removeentry",   3),
                "removeuser"   : ("m", "removeuser",    3),
                "listqueue"    : ("e", "listentries",   3),
                "listusers"    : ("m", "listusers",     5),
                "jbqueue"      : ("m", "jbqueue",       3),
                "jdqueue"      : ("m", "jdqueue",       3),
                "currentsong"  : ("e", "currententry", 10),
                "queue"        : ("e", "status",        0),
                "played"       : ("e", "picked",        3),
                "pick"         : ("m", "pickentry",     3),
                "help"         : ("e", "help",         10),
                "testqueue"    : ("m", "testqueue",     5),
                "queueconfirm" : ("m", "queueconfirm",  0),
                }
        self.cooldowns = {}
        self.aliases = {
                "sr"          : ("join",),
                "listqueue"   : ("queuelist",),
                "played"      : ("picked",),
                "removesong"  : ("removeentry",),
                "currentsong" : ("currentuser",),
                "testqueue"   : ("queuetest",),
                "queueconfirm": ("confirmqueue",),
                }

    def __getitem__(self, attr):
        """Searches for a method maching the given request"""
        return getattr(self.mthds, attr, None)

    def check_aliases(self, command):

        res = [
                k for k in self.aliases
                if command in self.aliases[k]
                ]
        return (res[0] if res else command)

    def check_cooldowns(self, command):
        current = time.time()
        timeleft = current - self.cooldowns.get(command[1], 0) - command[2]
        if timeleft >= 0:
            self.cooldowns[command[1]] = current
            return True
        else:
            print(
                    col(
                        f"'{command[1]}' still on cooldown for "
                        + f"{round(timeleft, 1) * -1}s",
                        "GREY"
                        )
                    )
            return False

    def find_command(self, badges, request, *alternatives):
        """
        Attempts to find methods matching the commands dict

        If the command is a moderator command, check that the badges
        contain an appropriate moderator - level badge
        """
        request = self.check_aliases(request.lower())
        command = self.commands.get(request, None)
        if command:
            if self.check_cooldowns(command):
                try:
                    for obj in (self,) + alternatives:
                        mthd = obj[command[1]]
                        if mthd:
                            raise CommandFound()
                except CommandFound:
                    if command[0] == "m":
                        if role_check(badges):
                            return mthd
                        else:
                            return None
                    else:
                        return mthd
            else:
                return None
        else:
            return None


def format_badges(tags):
    """Checks a tags dict for roles and outputs coloured markers if found"""
    badges = tags['badges']
    res = ''
    roles = [
            ("RED",    ("broadcaster",),          "B"),
            ("GREEN",  ("moderator",),            "M"),
            ("BLUE",   ("subscriber", "premium"), "S"),
            ("PURPLE", ("vip",),                  "V"),
            ]

    for role in roles:
        res += (col(role[2], role[0]) if role_check(badges, *role[1]) else '')
    return res


def role_check(badges, *roles):
    """Processes a badges string for the given roles"""
    if not roles:
        roles = ["moderator", "broadcaster"]
    try:
        return any([
                role in badge
                for badge in badges.split(",")
                for role in roles
                ])
    except AttributeError:
        return False
