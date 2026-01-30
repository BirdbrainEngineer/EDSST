from src.modules import module
from prompt_toolkit.styles import Style
import asyncio
from typing import Any


class ChatboxRelay(module.Module): 
    style = Style.from_dict({   # The KeyValue-s in this dictionary can be accessed as html tag modifiers in self.print
        "module_color": "#a0a0a0",              # Example: self.print(f"<module_color>Hello World.</module_color>")
    })

    MODULE_NAME: str = "ChatBoxRelay"
    MODULE_VERSION: str = "0.0.1"

    def __init__(self) -> None:
        super().__init__()

    async def process_event(self, event: Any, event_raw: str, tg: asyncio.TaskGroup) -> None:   # Events are either new journal file lines or events produced by EDSST
        await super().process_event(event, event_raw, tg)
        match event["event"]:   # Events are currently passed as dict[str, Any]
            case "SendText": 
                if event["To"] == "Local":
                    #push_user_input(event["Message"])
                    pass
            case _: pass

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        if arguments[0] in ["chatrelay", "chatboxrelay", "textrelay", "commsrelay"]:   # Currently this is the way to define extra aliases for your module
            match arguments[1]:
                case "start":
                    self.listening = True
                case "stop":
                    self.listening = False
                case "enable":
                    self.enable()
                case "disable":
                    self.disable()
                case _: pass