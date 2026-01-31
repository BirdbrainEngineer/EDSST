from src.modules import module
from prompt_toolkit.styles import Style
import asyncio
from typing import Any, Callable

class ChatboxRelayState(module.ModuleState):
    listening: bool = False

class ChatboxRelay(module.Module): 
    style = Style.from_dict({  
        "module_color": "#a0a0a0",
        "ingame": "#FF8000 bold",
    })

    MODULE_NAME: str = "ChatboxRelay"
    MODULE_VERSION: str = "0.1.0"
    STATE_TYPE = ChatboxRelayState
    state: ChatboxRelayState
    push_user_input: Callable[[asyncio.TaskGroup, str], Any]

    def __init__(self, user_input_pusher: Callable[[asyncio.TaskGroup, str], Any]) -> None:
        super().__init__()
        self.push_user_input = user_input_pusher

    async def process_event(self, event: dict[str, Any], event_raw: str, tg: asyncio.TaskGroup) -> None:   # Events are either new journal file lines or events produced by EDSST
        await super().process_event(event, event_raw, tg)
        match event["event"]:   # Events are currently passed as dict[str, Any]
            case "SendText": 
                self.print(str(event))
                if event["To"] == "local":
                    self.print(f"{event["Message"]}", prefix="<ingame>&gt;&gt;&gt; </ingame>")
                    await self.push_user_input(tg, event["Message"])
            case _: pass

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        if arguments[0] in ["chatrelay", "chatboxrelay", "textrelay", "commsrelay", "chat"]:   # Currently this is the way to define extra aliases for your module
            match arguments[1]:
                case "start":
                    self.print("<green>Now listening to your messages in local chat.</green>")
                    self.state.listening = True
                case "stop":
                    self.print("<yellow>No longer listening to your messages in local chat.</yellow>")
                    self.state.listening = False
                case "enable":
                    self.enable()
                case "disable":
                    self.disable()
                case _: pass