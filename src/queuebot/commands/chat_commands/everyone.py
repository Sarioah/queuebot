from __future__ import annotations

from typing import TYPE_CHECKING

from queuebot.commands.chat_commands import ChatCommandEvent

if TYPE_CHECKING:
    from queuebot.coordinator import Coordinator


def derp(cord: Coordinator):
    cord.handle_chat_event(ChatCommandEvent())
