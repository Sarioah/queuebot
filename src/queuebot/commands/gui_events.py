from dataclasses import dataclass
from typing import TypeAlias

from queuebot.state.state_management import QueueMode


@dataclass(slots=True)
class EntryPicked:
    entry_id: int


@dataclass(slots=True)
class EntryDeleted:
    entry_id: int


@dataclass(slots=True)
class ModeChange:
    mode: QueueMode


@dataclass(slots=True)
class QueueCleared:
    pass


@dataclass(slots=True)
class QueueRandomised:
    pass


@dataclass(slots=True)
class QueueToggle:
    state: bool


GuiCommandEvent: TypeAlias = (
    EntryPicked | EntryDeleted | ModeChange | QueueCleared | QueueToggle | QueueRandomised
)
