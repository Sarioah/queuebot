#!/usr/bin/python3
"""Retrieve emote strings from FrankerFaceZ and BTTV for the given channels."""
import asyncio
import json
import sys

import aiohttp
from aiohttp.client_exceptions import ClientError
from aiohttp.http_websocket import WebSocketError
from aiohttp.streams import EofStream

MIN_VERSION = 3, 8
if all(
    [
        sys.version_info[0] == MIN_VERSION[0],
        sys.version_info[1] >= MIN_VERSION[1],
        sys.platform.startswith("win"),
    ]
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

IGNORABLE_IO_EXCEPTIONS = (
    ClientError,
    WebSocketError,
    EofStream,
    OSError,
    ValueError,
    AttributeError,
    LookupError,
    StopAsyncIteration,
)


async def _get(url):
    async with aiohttp.ClientSession() as session:
        return await (await session.get(url)).text()


async def _get_ffz(channel="__ffz_global"):
    try:
        j = json.loads(await _get(f"https://api.frankerfacez.com/v1/room/{channel}"))
        j = [
            emote["name"]
            for set_name, emote_set in j["sets"].items()
            for emote in emote_set["emoticons"]
        ]
    except IGNORABLE_IO_EXCEPTIONS:
        j = []
    if channel != "__ffz_global":
        channel += "__ffz"
    return {channel: j}


async def _get_bttv(channel=""):
    try:
        if not channel:
            channel = "__bttv_global"
            j = json.loads(
                await _get("https://api.betterttv.net/3/cached/emotes/global")
            )
            j = [emote["code"] for emote in j]
        else:
            twitch_channel, channel = channel, channel + "__bttv"
            bttv_id = json.loads(
                await _get(f"https://decapi.me/twitch/id/{twitch_channel}")
            )
            j = json.loads(
                await _get(f"https://api.betterttv.net/3/cached/users/twitch/{bttv_id}")
            )
            j = [
                emote["code"]
                for emote_set in ("channelEmotes", "sharedEmotes")
                for emote in j[emote_set]
            ]
    except IGNORABLE_IO_EXCEPTIONS:
        j = []
    return {channel: j}


async def _main(channels=()):
    tasks = [_get_ffz(), _get_bttv()]
    for channel in channels:
        tasks += [_get_ffz(channel), _get_bttv(channel)]
    return await asyncio.gather(*tasks)


def get_emotes(*channels: str) -> dict[str, list]:
    """Return a dict of lists of emote strings for the given channels.

    Lists can potentially be empty.

    Example dict structure after calling get_emotes('channel1', 'channel2'):
    {
        '__ffz_global': ['Kappa', 'ManChicken', 'SomeEmote'],
        '__bttv_global': ['LuL', 'SoSnowy'],
        'channel1__ffz': ['channel1LUL', 'channel1Kappa'],
        'channel1__bttv': ['channel1OMG'],
        'channel2__ffz': [],
        'channel2__bttv': ['channel2Emote', 'channel2LUL']
    }

    Args:
        channels: Collects channel names.

    Returns:
        Dict of Lists of emote strings grouped by channel.
    """
    return {k: v for d in asyncio.run(_main(channels)) for k, v in d.items()}


if __name__ == "__main__":
    emotes = get_emotes(*sys.argv[1:])
    print(json.dumps(emotes, indent=4))
