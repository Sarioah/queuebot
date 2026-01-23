import unittest
from configparser import ParsingError
from unittest.mock import Mock, patch

from queuebot.tools import config

DEFAULTS = {
    "bot_name": "********",
    "channel": "********",
    "bot_prefix": "!",
    "muted": "False",
    "logging": "False",
    "startup_msg": "True",
}


# ruff: noqa: D101, D102
class TestPasswordHandler(unittest.TestCase):
    @patch("queuebot.tools.config.keyring")
    def setUp(self, mock_keyring):
        self.mock_keyring = mock_keyring
        self.mock_keyring.get_password.return_value = "example_password"
        self.p_h = config.PasswordHandler("example_user")

    @patch("queuebot.tools.config.keyring")
    @patch("builtins.input")
    def test_no_passwd(self, mocked_input, mocked_keyring):
        mocked_input.return_value = "example_token"
        mocked_keyring.get_password.side_effect = None, "example_token"
        with patch("builtins.print") as mocked_print:
            config.PasswordHandler("example_user")
        mocked_input.assert_called_with(
            "Input your oauth code, including the 'oauth:' at the front: "
        )
        mocked_print.assert_called_with(
            "Please log into twitch using your bot account, then visit "
            "\x1b[34;1mhttps://twitchapps.com/tmi:\x1b[0m to generate an "
            "oauth code for the bot to login with. Then paste it here and press enter.\n"
        )
        mocked_keyring.get_password.assert_called_with("TMI", "example_user")
        mocked_keyring.get_password.assert_called_with("TMI", "example_user")
        mocked_keyring.set_password.assert_called_with("TMI", "example_user", "example_token")
        self.assertGreater(mocked_keyring.get_password.call_count, 1)

    @patch("queuebot.tools.config.keyring")
    def test_del_password(self, mock_keyring):
        self.p_h.del_password()
        mock_keyring.delete_password.assert_called_once_with("TMI", "example_user")


@patch("builtins.open")
@patch("queuebot.tools.config.ConfigParser")
class TestConfiguration(unittest.TestCase):
    def test_init_problem(self, mock_parser, _mock_open):
        mock_parser.return_value.__getitem__ = default_config_factory()
        self.assertRaises(Exception, config.Configuration, "example_config_filename")
        mock_parser.assert_called_with()
        mock_parser().read.assert_called_with("example_config_filename")

    def test_init_correctly(self, mock_parser, mock_open):
        defaults = {k: v for k, v in DEFAULTS.items()}
        defaults["bot_name"] = "example_user"
        defaults["channel"] = "example_channel"
        mock_parser.return_value.__getitem__ = default_config_factory(defaults)
        configuration = config.Configuration("example_config_filename")
        self.assertIsInstance(configuration, config.Configuration)
        self.assertEqual(configuration.get_config(), defaults)

        mock_file_handle = Mock()
        mock_open.return_value.__enter__.return_value = mock_file_handle
        configuration.write_config()
        mock_parser.return_value.write.assert_called_with(mock_file_handle)

    def test_mis_formatted_config(self, mock_parser, _mock_open):
        def _side_effect(*_args):
            raise ParsingError("Mocked error")

        mock_parser.return_value.read.side_effect = _side_effect
        self.assertRaises(Exception, config.Configuration, "example_config_filename")
        mock_parser().read.assert_called_with("example_config_filename")

    def test_empty_config(self, mock_parser, _mock_open):
        mock_parser.return_value.__getitem__.return_value = {}
        self.assertRaises(Exception, config.Configuration, "example_config_filename")

    def test_missing_config_section(self, mock_parser, _mock_open):
        defaults = {k: v for k, v in DEFAULTS.items()}
        del defaults["bot_name"]
        del defaults["channel"]
        mock_parser.return_value.__getitem__ = default_config_factory(defaults)
        self.assertRaises(Exception, config.Configuration, "example_config_filename")


class TestConfigFunctions(unittest.TestCase):
    @patch("queuebot.tools.config.urlopen")
    def test_check_update(self, mock_urlopen):
        mock_urlopen.return_value.__enter__.return_value.read.return_value = '{"name": "1.3"}'
        self.assertIsNone(config.check_update("1.4"))
        self.assertIsNone(config.check_update("1.3"))
        self.assertEqual(
            config.check_update("1.2"),
            'Updated bot found, version "\x1b[34;1m1.3\x1b[0m".\nPlease visit '
            "\x1b[33;1mhttps://github.com/Sarioah/queuebot/releases/latest\x1b[0m "
            "to download the new bot",
        )
        self.assertEqual(len(mock_urlopen.mock_calls), 12)
        mock_urlopen.assert_called_with(
            "https://api.github.com/repos/sarioah/queuebot/releases/latest", timeout=3
        )


def default_config_factory(defaults=None):
    """Create functions suitable for use as a mock __getitem__."""
    if defaults is None:
        defaults = DEFAULTS
    config = {"DEFAULT": defaults}

    def get_item(_obj, item):
        return config[item]

    return get_item
