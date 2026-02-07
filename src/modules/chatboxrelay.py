from src.modules import module
from prompt_toolkit.styles import Style
import asyncio
from typing import Any, Callable
from src.version import TESTING_MODE, TestingMode

class ChatboxRelayState(module.ModuleState):
    is_listening: bool = False

class ChatboxRelay(module.Module): 
    style = Style.from_dict({  
        "module_color": "#a0a0a0",
        "ingame": "#FF8000 bold",
    })

    MODULE_NAME: str = "ChatboxRelay"
    MODULE_VERSION: str = "0.1.2"
    EXTRA_ALIASES: set[str] = set(["chat", "chatrelay", "textrelay", "commsrelay"])
    STATE_TYPE = ChatboxRelayState
    state: ChatboxRelayState
    push_user_input: Callable[[asyncio.TaskGroup, str], Any]

    def __init__(self, user_input_pusher: Callable[[asyncio.TaskGroup, str], Any]) -> None:
        super().__init__(self.EXTRA_ALIASES)
        if not self.state.enabled:
            self.enable()
        self.push_user_input = user_input_pusher

    async def process_event(self, event: dict[str, Any], tg: asyncio.TaskGroup) -> None:   # Events are either new journal file lines or events produced by EDSST
        await super().process_event(event, tg)
        match event["event"]:   # Events are currently passed as dict[str, Any]
            case "SendText": 
                if self.caught_up:
                    if TESTING_MODE == TestingMode.Testing: self.print(str(event))
                    if event["To"] == "local":
                        self.print(f"{event["Message"]}", prefix="<ingame>&gt;&gt;&gt; </ingame>")
                        await self.push_user_input(tg, event["Message"])
            case "CaughtUp":
                if self.state.enabled:
                    if self.state.is_listening:
                        self.print("<green>Currently listening to your messages in local chat!</green>")
                    else:
                        self.print("<yellow>Currently not listening to in-game chat!</yellow>")
            case _: pass

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None: # Currently this is the way to define extra aliases for your module
        await super().process_user_input(arguments, tg)
        match arguments[1]:
            case "start" | "listen" | "begin":
                self.print("<green>Now listening to your messages in local chat.</green>")
                self.state.is_listening = True
            case "stop" | "deafen" | "end":
                self.print("<yellow>No longer listening to your messages in local chat.</yellow>")
                self.state.is_listening = False
            case _: pass