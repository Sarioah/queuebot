import json
import unittest
from unittest.mock import AsyncMock, call, patch

from tools import get_emotes


# ruff: noqa: D102
class TestGet(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mocked_url = "https://example.com"
        self.mocked_text = "Example text"
        patcher = patch("aiohttp.ClientSession")
        self.addCleanup(patcher.stop)
        self.mocked_client_session = patcher.start()
        self.mocked_get = AsyncMock()
        self.mocked_client_session.return_value.__aenter__.return_value.get = (
            self.mocked_get
        )
        self.set_mocked_get_text(self.mocked_text)

    def set_mocked_get_text(self, /, *text, multiple=False):
        if multiple:
            self.mocked_get.return_value.text.return_value = None
            self.mocked_get.return_value.text.side_effect = text
        else:
            self.mocked_get.return_value.text.return_value = text[0]

    async def test_get(self):
        res = await get_emotes._get(self.mocked_url)
        self.mocked_client_session.assert_called_with()
        self.mocked_get.assert_awaited_with(self.mocked_url)
        self.assertEqual(res, self.mocked_text)

    async def test_get_ffz(self):
        await get_emotes._get_ffz()
        self.mocked_get.assert_awaited_with(
            "https://api.frankerfacez.com/v1/room/__ffz_global"
        )

        self.set_mocked_get_text(
            json.dumps(
                {
                    "sets": {
                        "global": {
                            "emoticons": [{"name": "ffzTest"}, {"name": "ffzTest2"}]
                        }
                    }
                }
            )
        )
        res = await get_emotes._get_ffz("test_name")
        self.mocked_get.assert_awaited_with(
            "https://api.frankerfacez.com/v1/room/test_name"
        )
        self.assertEqual(res, {"test_name__ffz": ["ffzTest", "ffzTest2"]})

        self.set_mocked_get_text("{}")
        res = await get_emotes._get_ffz()
        self.assertEqual(res, {"__ffz_global": []})

    async def test_get_bttv(self):
        self.set_mocked_get_text(json.dumps([{"code": "test1"}, {"code": "test2"}]))
        res = await get_emotes._get_bttv()
        self.assertEqual(res, {"__bttv_global": ["test1", "test2"]})
        self.mocked_get.assert_awaited_with(
            "https://api.betterttv.net/3/cached/emotes/global"
        )

        self.set_mocked_get_text(
            '"example_userid"',
            json.dumps(
                {
                    "channelEmotes": [
                        {"code": "exampleTest1"},
                        {"code": "exampleTest2"},
                    ],
                    "sharedEmotes": [
                        {"code": "exampleTest3"},
                        {"code": "exampleTest4"},
                    ],
                }
            ),
            multiple=True,
        )
        res = await get_emotes._get_bttv("example_username")
        self.assertEqual(
            res,
            {
                "example_username__bttv": [
                    "exampleTest1",
                    "exampleTest2",
                    "exampleTest3",
                    "exampleTest4",
                ]
            },
        )
        self.mocked_get.assert_has_awaits(
            [
                call("https://decapi.me/twitch/id/example_username"),
                call("https://api.betterttv.net/3/cached/users/twitch/example_userid"),
            ],
            any_order=False,
        )
        self.set_mocked_get_text("not json parseable")
        res = await get_emotes._get_bttv()
        self.assertEqual(res, {"__bttv_global": []})

    async def test_main(self):
        self.assertEqual(
            await get_emotes._main(), [{"__ffz_global": []}, {"__bttv_global": []}]
        )
        self.assertEqual(
            await get_emotes._main(("example_username1", "example_username2")),
            [
                {"__ffz_global": []},
                {"__bttv_global": []},
                {"example_username1__ffz": []},
                {"example_username1__bttv": []},
                {"example_username2__ffz": []},
                {"example_username2__bttv": []},
            ],
        )

    def test_get_emotes(self):
        self.assertEqual(
            get_emotes.get_emotes(), {"__ffz_global": [], "__bttv_global": []}
        )
        self.assertEqual(
            get_emotes.get_emotes("example_username1", "example_username2"),
            {
                "__ffz_global": [],
                "__bttv_global": [],
                "example_username1__ffz": [],
                "example_username1__bttv": [],
                "example_username2__ffz": [],
                "example_username2__bttv": [],
            },
        )
