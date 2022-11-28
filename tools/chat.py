"""Tools for chat based commands, text manipulation and output formatting."""
import time

from tools.text import colourise as col


class Commands:
    """Object holding generic commands that aren't bound methods elsewhere."""

    def __init__(self, parent):
        """Create a Commands object.

        Args:
            parent: Namespace to search through for additional commands.
        """
        self.parent = parent

    def help(self, *_args):
        """List available chat commands."""
        everyone = [k for k in self.parent.commands if self.parent.commands[k][0] == "e"]
        mods = [k for k in self.parent.commands if self.parent.commands[k][0] == "m"]
        return (
            f"Queuebot commands: \"{', '.join(everyone)}\" "
            + f"• Queuebot moderator commands: \"{', '.join(mods)}\""
        )

    def listaliases(self, *_args):
        """List available command aliases."""
        # TODO: Need to guard this and help against IRC msg limit

        return "Aliases: " + " • ".join(
            ", ".join(alias for alias in value) + f' -> "{key}"'
            for key, value in self.parent.aliases.items()
        )


class CommandHandler:
    """Maps chat commands to methods bound to objects like a SongQueue."""

    def __init__(self):
        """Create a CommandHandler object."""
        self.mthds = Commands(self)
        self.commands = {
            "sr": ("e", "addentry", 0),
            "leave": ("e", "leave", 0),
            "openqueue": ("m", "open", 3),
            "closequeue": ("m", "close", 3),
            "clearqueue": ("m", "clear", 3),
            "clearparty": ("m", "clearparty", 3),
            "removesong": ("m", "removeentry", 3),
            "removeuser": ("m", "removeuser", 3),
            "listqueue": ("e", "listentries", 3),
            "listusers": ("m", "listusers", 3),
            "jbqueue": ("m", "jbqueue", 3),
            "jdqueue": ("m", "jdqueue", 3),
            "currentsong": ("e", "currententry", 3),
            "queue": ("e", "status", 0),
            "played": ("e", "picked", 3),
            "pick": ("m", "pickentry", 1),
            "help": ("e", "help", 10),
            "whichsong": ("e", "lookupentry", 3),
            "whichuser": ("e", "lookupuser", 3),
            "listaliases": ("e", "listaliases", 10),
            "testqueue": ("m", "testqueue", 10),
            "queueconfirm": ("m", "queueconfirm", 0),
        }
        self.cooldowns = {}
        self.aliases = {
            "sr": ("join",),
            "listqueue": ("queuelist",),
            "clearparty": ("cleargroup", "clearusers"),
            "played": ("picked",),
            "removesong": ("removeentry",),
            "currentsong": (
                "currentuser",
                "currentusers",
                "currentparty",
                "currentgroup",
            ),
            "testqueue": ("queuetest",),
            "whichsong": ("queuesong",),
            "whichuser": ("queueuser",),
            "jbqueue": ("priorityqueue",),
            "jdqueue": ("randomqueue",),
            "queueconfirm": ("confirmqueue",),
        }

    def __getitem__(self, attr):
        """Search for a method maching the specified attribute name."""
        return getattr(self.mthds, attr, None)

    def check_aliases(self, command):
        """Check if a chat command matches an alias of a known method.

        Args:
            command: Name of command to find alias' for.

        Returns:
            Command that matches the given alias, otherwise returns the
                original search term.
        """
        res = [key for key, value in self.aliases.items() if command in value]
        return res[0] if res else command

    def check_cooldowns(self, command):
        """Check that a chat command is waiting for a cooldown to expire.

        Args:
            command: Command name to check.

        Returns:
            True if command's cooldown has already expired, otherwise prints a
                message and returns False.
        """
        current = time.time()
        timeleft = current - self.cooldowns.get(command[1], 0) - command[2]
        if timeleft >= 0:
            self.cooldowns[command[1]] = current
            return True
        print(col(f"'{command[1]}' still on cooldown for {round(timeleft, 1) * -1}s", "GREY"))
        return False

    def find_command(self, badges, request, *alternatives):
        """Attempt to find a method present in the commands dictionary.

        If the command is a moderator command, check that the badges contain an
        appropriate moderator - level badge.

        Command handling objects can define command / request names to ignore
        as a list in an "exclusions" attribute.

        Args:
            badges: List of strings representing chat badges owned by the
                chatter who sent the command.
            request: Name of command to search for.
            alternatives: Extra objects to look through for commands.

        Returns:
            Command name if command found, not on a cooldown and the chatter is
            eligible to use it.
        """
        # TODO: Revisit this again, as well as the convoluted Event class
        command_name = self.check_aliases(request.casefold())

        command = self.commands.get(command_name, None)
        if command and self.check_cooldowns(command):
            for obj in (self,) + alternatives:
                exclusions = getattr(obj, "exclusions", [])
                if request.casefold() in exclusions:
                    return None
                mthd = obj[command[1]]
                if mthd:
                    if command[0] == "m":
                        if role_check(badges):
                            return mthd
                    return mthd
        return None


def format_badges(tags):
    """Check a tags dict for roles and outputs coloured markers if found.

    Args:
        tags: Dict containing metadata of a chat message.

    Returns:
        String formatted with coloured letters representing roles found in the
        message tags.
    """
    # TODO: roles as dict maybe, probably a comprehension to generate the
    # coloured suffix
    badges = tags["badges"]
    res = ""
    roles = [
        ("RED", ("broadcaster",), "B"),
        ("GREEN", ("moderator",), "M"),
        ("BLUE", ("subscriber", "premium"), "S"),
        ("PURPLE", ("vip",), "V"),
    ]

    for role in roles:
        res += col(role[2], role[0]) if role_check(badges, *role[1]) else ""
    return res


def role_check(badges, *roles):
    """Process a badges string for the given roles.

    Args:
        badges: List of strings representing chat badges on a chat messsage.
        roles: Roles to check for in the chat badges.

    Returns:
        True if at least one of the roles were found in the chat badges. If
        roles tuple was empty, returns True if moderator level badges found.
    """
    if not roles:
        roles = ["moderator", "broadcaster"]
    try:
        return any(role in badge for badge in badges.split(",") for role in roles)
    except AttributeError:
        return False
