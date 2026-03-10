from dataclasses import dataclass, field
from typing import Callable

from queuebot.state.state_management import QueueMode, QueueState

from .commands.chat_commands import ChatCommandEvent
from .commands.gui_events import (
    EntryDeleted,
    EntryPicked,
    GuiCommandEvent,
    ModeChange,
    QueueCleared,
    QueueRandomised,
    QueueToggle,
)
from .state.song_queue import SongQueue


@dataclass
class Coordinator:
    state: SongQueue
    ui_state: QueueState
    ui_handler: Callable = field(init=False)

    def subscribe_ui_handler(self, handler: Callable):
        self.ui_handler = handler

    def notify_ui(self, event):
        self.ui_handler(event)

    def handle_chat_event(self, event: ChatCommandEvent):
        print(f"sent command {event}")

    def handle_gui_event(
        self, event: GuiCommandEvent, callback: Callable[[QueueState], None]
    ) -> None:
        res = ""
        match event:
            case EntryPicked(e_id):
                res = self.state.pickentry(None, e_id)
            case EntryDeleted(e_id):
                print(e_id)
                res = self.state.removeentry(None, e_id)
            case ModeChange(mode):
                res = self.state.jdqueue() if mode == QueueMode.REQUEST else self.state.jbqueue()
            case QueueCleared():
                res = self.state.clear()
            case QueueToggle(state):
                res = self.state.open() if state else self.state.close()
            case QueueRandomised():
                res = self.state.randomise(None, 17)
            case _:
                raise NotImplementedError("Command not handled")
        if res:
            print(res)
        self.state.save()
        self.ui_state = self.state.as_ui_state()
        callback(self.ui_state)
