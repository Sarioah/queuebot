#!/usr/bin/python3
import json
import sys

import asyncio
import aiohttp


if (
    sys.version_info[0] == 3
    and sys.version_info[1] >= 8
    and sys.platform.startswith("win")
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def _get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


async def _get_ffz(channel='__ffz_global'):
    try:
        j = json.loads(
            await _get(
                f"https://api.frankerfacez.com/v1/room/{channel}"
            )
        )
        j = [
            emote['name']
            for emote_set in j['sets']
            for emote in j['sets'][emote_set]['emoticons']
        ]
    except Exception:
        j = []
    if channel != '__ffz_global':
        channel += "__ffz"
    return {channel: j}


async def _get_bttv(channel=''):
    try:
        if not channel:
            channel = '__bttv_global'
            j = json.loads(
                await _get(
                    "https://api.betterttv.net/3/cached/emotes/global"
                )
            )
            j = [emote['code'] for emote in j]
        else:
            twitch_channel, channel = channel, channel + "__bttv"
            bttv_id = json.loads(
                await _get(
                    f"https://decapi.me/twitch/id/{twitch_channel}"
                )
            )
            j = json.loads(
                await _get(
                    "https://api.betterttv.net/3/cached/users/twitch/"
                    f"{bttv_id}"
                )
            )
            j = [
                emote['code']
                for emote_set in ('channelEmotes', 'sharedEmotes')
                for emote in j[emote_set]
            ]
    except Exception:
        j = []
    return {channel: j}


async def _main(channels):
    tasks = [_get_ffz(), _get_bttv()]
    for channel in channels:
        tasks += [_get_ffz(channel), _get_bttv(channel)]
    return await asyncio.gather(*tasks)


def get_emotes(*channels):
    res = {
        k: d[k]
        for d in asyncio.run(_main(channels))
        for k in d
        }
    return res


if __name__ == "__main__":
    emotes = get_emotes(*sys.argv[1:])
    print(emotes)
