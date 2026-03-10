from dataclasses import dataclass, field
from enum import Enum, auto


class QueueMode(Enum):
    REQUEST = auto()
    USER = auto()


@dataclass
class Request:
    user: str
    request: str


@dataclass
class QueueState:
    queue_open: bool = False
    queue_mode: QueueMode = QueueMode.REQUEST
    current_pick: Request | None = None
    queue_items: list[Request] = field(default_factory=list)
    picked_items: list[Request] = field(default_factory=list)
