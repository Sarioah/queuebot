from dataclasses import dataclass, field
from functools import partial
from random import choice, randint

import faker
from nicegui import ui

from queuebot.coordinator import Coordinator
from queuebot.state.state_management import QueueMode, QueueState, Request

from ..commands.gui_events import (
    EntryDeleted,
    EntryPicked,
    GuiCommandEvent,
    ModeChange,
    QueueCleared,
    QueueRandomised,
    QueueToggle,
)

gui_started = False


def set_started():
    global gui_started
    gui_started = True
    print("ui has loaded")


@dataclass
class QueuebotUI:
    coord: Coordinator = field(init=False)
    state: QueueState = field(default_factory=QueueState)
    updating: bool = False

    chat_log: ui.log = field(init=False)
    current: ui.row = field(init=False)
    pending: ui.card = field(init=False)
    picked: ui.card = field(init=False)

    tgl_queue_enable: ui.toggle = field(init=False)
    tgl_queue_mode: ui.toggle = field(init=False)

    btn_pick: ui.button = field(init=False)

    def _draw_current(self):
        with self.current as curr:
            curr.clear()
            ui.icon("radio").classes("text-primary text-2xl")
            ui.label("Current pick:").classes("font-bold")
            if self.state.current_pick:
                ui.label(self.state.current_pick.user).classes("font-bold text-primary")
                ui.label("--").classes("text-grey")
                ui.label(self.state.current_pick.request).classes("italic")

    def _draw_pending(self):
        with self.pending as pending:
            pending.clear()
            with ui.row().classes("flex flex-nowrap justify-around items-center w-full"):
                ui.label("User requests").classes("flex-1 font-bold")
                with ui.row().classes("flex-1 justify-end items-center w-full gap-2"):
                    ui.label("users:").classes("text-sm text-grey-7")
                    ui.label(str(len(self.state.queue_items))).classes("font-bold text-lg")
            ui.separator()
            with ui.scroll_area().classes("flex-1 min-h-0 w-full"):
                # pending area
                with ui.column().classes("w-full gap-2"):
                    for i, request in enumerate(self.state.queue_items):
                        self._add_request_card(entry_id=i, request=request)

    def _draw_picked(self):
        with self.picked as picked:
            picked.clear()
            with ui.row().classes("flex flex-nowrap justify-around items-center w-full"):
                ui.label("Picked requests").classes("flex-1 font-bold")
                with ui.row().classes("flex-1 justify-end items-center w-full gap-2"):
                    ui.label("picked:").classes("text-sm text-grey-7")
                    ui.label(str(len(self.state.picked_items))).classes("font-bold text-lg")
            ui.separator()
            with ui.scroll_area().classes("flex-1 min-h-0 w-full"):
                # picked area
                with ui.column().props("id=picked").classes("w-full gap-2"):
                    for request in self.state.picked_items:
                        self._add_picked_card(request=request)

    def _update_controls(self):
        self.tgl_queue_enable.on_value_change(lambda: None)
        self.tgl_queue_mode.on_value_change(lambda: None)
        self.tgl_queue_enable.set_value("open" if self.state.queue_open else "closed")
        self.tgl_queue_mode.set_value(
            "request" if self.state.queue_mode == QueueMode.REQUEST else "user"
        )
        self.btn_pick.text = (
            "Pick Random" if self.state.queue_mode == QueueMode.REQUEST else "Pick User"
        )
        self.btn_pick.enabled = len(self.state.queue_items) > 0

    def send_command(self, command: GuiCommandEvent):
        if gui_started and not self.updating:
            self.coord.handle_gui_event(command, self.update)

    def handle_event(self):
        pass

    def add_coordinator(self, coord):
        self.coord = coord

    def update(self, state: QueueState):
        self.updating = True
        self.state = state
        self._draw_current()
        self._draw_pending()
        self._draw_picked()
        self._update_controls()
        self.updating = False

    def reset(self):
        self._randomise_state()
        self.update(self.state)

    def _randomise_state(self):
        self.state = QueueState(
            queue_open=choice((True, False)),
            queue_mode=choice(list(QueueMode)),
            current_pick=Request(
                f"user {randint(1, 6)}",
                " ".join(faker.Faker().words(randint(4, 15))),
            ),
            queue_items=[
                Request(f"example user {i}", " ".join(faker.Faker().words(randint(4, 25))))
                for i in range(1, randint(4, 7))
            ],
            picked_items=[
                Request(f"example user {i}", " ".join(faker.Faker().words(randint(4, 25))))
                for i in range(1, randint(4, 7))
            ],
        )

    def _reset_state(self):
        self.state = QueueState()

    def _pick_entry(self, entry_id):
        entry = self.state.queue_items.pop(entry_id)
        self.state.current_pick = entry
        self.state.picked_items.append(entry)
        self.update()

    def _delete_entry(self, entry_id):
        self.state.queue_items.pop(entry_id)
        self.update()

    def _add_request_card(
        self, entry_id=None, request=Request("example user", "this is their example request")
    ):
        with ui.card().classes("w-full"):
            with ui.row().classes("w-full items-center justify-between"):
                with ui.column().classes("w-full flex-1 gap-0"):
                    ui.label(request.user).classes("font-bold text-sm")
                    ui.label(request.request).classes("italic")
                with ui.column().classes("p-0 gap-1"):
                    ui.button(
                        icon="check", on_click=partial(self.send_command, EntryPicked(entry_id))
                    ).props("rounded size=xs").classes("w-full")
                    ui.button(
                        icon="delete", on_click=partial(self.send_command, EntryDeleted(entry_id))
                    ).props("rounded outline color=negative size=xs").classes("w-full")

    def _add_picked_card(self, request=Request("example user", "this is their example request")):
        with ui.card().classes("w-full"):
            with ui.row().classes("w-full items-center justify-between"):
                with ui.column().classes("w-full flex-1 gap-0"):
                    ui.label(request.user).classes("font-bold text-sm")
                    ui.label(request.request).classes("italic")

    def build_page(self):
        # modify main element, set up flex and margins
        ui.query("body").classes("m-0 p-0")
        self.ui_container = ui.query("div.nicegui-content").classes(
            "flex flex-col h-screen w-screen p-0 gap-0"
        )

        # CURRENT PICK
        with ui.card().classes("w-full shrink-0"):
            # pick area
            self.current = ui.row().classes("w-full items-center gap-2 flex-wrap")
            self._draw_current()

        ui.separator().classes("my-2")
        # MAIN AREA
        with ui.element("div").classes("flex flex-row flex-7 flex-nowrap min-h-0 gap-2 w-full"):
            # LEFT SIDE: PENDING REQUESTS
            with ui.element("div").classes("flex flex-col flex-2 min-h-0 min-w-0"):
                self.pending = ui.card().classes(
                    "flex flex-col flex-1 min-h-0 w-full overflow-hidden"
                )
                self._draw_pending()

            # MIDDLE: CONTROLS
            with ui.element("div").classes("flex flex-col flex-1 min-h-0 min-w-50"):
                with ui.card().classes("flex flex-col w-full h-full overflow-hidden"):
                    ui.label("Controls").classes("font-bold")

                    ui.separator()
                    with ui.element("div").classes(
                        "flex flex-wrap justify-evenly items-center gap-2 w-full"
                    ):
                        self.tgl_queue_enable = ui.toggle(
                            {"open": "Open", "closed": "Closed"},
                            value="open",
                            on_change=lambda x: self.send_command(QueueToggle(x.value == "open")),
                        )
                        self.tgl_queue_mode = ui.toggle(
                            {"request": "Just Dance", "user": "User Queue"},
                            value="request",
                            on_change=lambda x: self.send_command(
                                ModeChange(
                                    QueueMode.REQUEST if x.value == "request" else QueueMode.USER
                                )
                            ),
                        )

                    ui.separator()
                    self.btn_pick = ui.button(
                        "Pick Random", on_click=partial(self.send_command, EntryPicked(None))
                    ).classes("w-full")
                    ui.button(
                        "Randomise Queue",
                        on_click=partial(self.send_command, QueueRandomised()),
                    ).classes("w-full")

                    ui.separator()
                    ui.button(
                        "Clear Queue", on_click=partial(self.send_command, QueueCleared())
                    ).props("outline").classes("w-full")
                    ui.button("Toggle Dark Mode", on_click=ui.dark_mode(value=True).toggle).props(
                        "outline"
                    ).classes("w-full")

                    ui.separator()
                    self._update_controls()

            # RIGHT SIDE: PICKED REQUESTS
            with ui.element("div").classes("flex flex-col flex-2 min-h-0 min-w-0"):
                self.picked = ui.card().classes("flex flex-col flex-1 w-full overflow-hidden")
                self._draw_picked()

        # LOWER DIV
        with ui.element("div").classes("flex flex-col flex-[3] min-h-0 w-full gap-2"):
            # DIVIDER LINE
            with ui.element("div").classes("flex items-center gap-2 shrink-0 w-full"):
                ui.separator().classes("flex-1")
                ui.label("CHAT LOG").classes("text-xs text-grey font-semibold")
                ui.separator().classes("flex-1")
            with ui.card().classes("flex flex-col flex-1 min-h-0 w-full overflow-hidden"):
                # chat log obj
                with ui.log(max_lines=200).classes(
                    "flex-1 min-h-0 text-xs font-mono"
                ) as self.chat_log:
                    self.chat_log.push("example message 1")
                    self.chat_log.push("example message 2")
                    self.chat_log.push("example message 3")


def build_ui() -> QueuebotUI:
    queue_ui = QueuebotUI()

    @ui.page("/")
    def index():
        queue_ui.build_page()
        ui.timer(0, set_started, once=True)
        ui.timer(0, lambda: queue_ui.update(queue_ui.state), once=True)

    return queue_ui
