import json
import unittest
from unittest.mock import Mock, patch

from queuebot.tools import chat

with open("src/queuebot/tests/tools/chat_testdata.json", "r", encoding="utf-8") as fd_:
    testdata = json.load(fd_)
    DATA = testdata["input"]
    EXPECTED_RESULTS = testdata["expected_results"]


# ruff: noqa: D101, D102
class TestChatCommands(unittest.TestCase):
    def setUp(self):
        self.mocked_parent = Mock()
        self.mocked_parent.commands = {
            "command1": ("e", "method1", 0),
            "command2": ("e", "method2", 3),
            "command3": ("m", "method3", 0),
            "command4": ("m", "method4", 3),
        }
        self.mocked_parent.aliases = {
            "command1": ("alternate1", "alternate2"),
            "command2": ("alternate3", "alternate4"),
            "command3": ("alternate5",),
        }
        self.c_c = chat.Commands(self.mocked_parent)

    def test_help(self):
        self.assertEqual(
            self.c_c.help(),
            'Queuebot commands: "command1, command2" • '
            'Queuebot moderator commands: "command3, command4"',
        )

    def test_list_aliases(self):
        self.assertEqual(
            self.c_c.list_aliases(),
            'Aliases: alternate1, alternate2 -> "command1" • '
            'alternate3, alternate4 -> "command2" • alternate5 -> "command3"',
        )


class TestChatCommandHandler(unittest.TestCase):
    @patch("queuebot.tools.chat.Commands")
    def setUp(self, mocked_commands):
        self.mocked_commands = mocked_commands
        self.c_h = chat.CommandHandler()

    def tearDown(self):
        self.mocked_commands.reset_mock()

    def test_get_item(self):
        self.assertIs(self.c_h["help"], self.mocked_commands.return_value.help)

    def test_check_aliases(self):
        for idx, alias in enumerate(DATA["check_aliases"]):
            self.assertEqual(
                self.c_h.check_aliases(alias),
                EXPECTED_RESULTS["check_aliases"][idx],
                f"Failed on '{alias}'",
            )

    @patch("builtins.print")
    def test_check_cooldowns(self, mocked_print):
        test_command_1 = ("m", "testcommand1", 3)
        test_command_2 = ("m", "testcommand2", 0)

        self.assertTrue(self.c_h.check_cooldowns(test_command_1))
        self.assertFalse(self.c_h.check_cooldowns(test_command_1))
        mocked_print.assert_called_with(
            f"\x1b[30;1m'{test_command_1[1]}' still on cooldown for {test_command_1[2]}.0s\x1b[0m"
        )
        mocked_print.reset_mock()
        self.assertTrue(self.c_h.check_cooldowns(test_command_2))
        self.assertTrue(self.c_h.check_cooldowns(test_command_2))
        mocked_print.assert_not_called()

    def test_find_command(self):
        self.assertIsNotNone(self.c_h.find_command("moderator,subscriber", "closequeue"))
        self.assertIsNone(self.c_h.find_command("vip,subscriber", "openqueue"))
        self.c_h.exclusions = ["sr"]
        self.assertIsNone(self.c_h.find_command("", "sr"))
        self.c_h.exclusions = []
        self.assertIsNotNone(self.c_h.find_command("", "sr"))


class TestChatFunctions(unittest.TestCase):
    def test_format_badges(self):
        for k, v in DATA["format_badges"].items():
            self.assertEqual(
                chat.format_badges(v),
                EXPECTED_RESULTS["format_badges"][k],
                f"Fail on '{k}'",
            )

    def test_role_check(self):
        self.assertRaises(TypeError, chat.role_check)
        self.assertFalse(chat.role_check([]))
        self.assertFalse(chat.role_check("subscriber,vip"))
        self.assertTrue(chat.role_check("subscriber,vip", "vip", "regular"))
        self.assertTrue(chat.role_check("moderator"))
        self.assertTrue(chat.role_check("subscriber,moderator"))
        self.assertTrue(chat.role_check("broadcaster"))
