from src.modules import module
from prompt_toolkit.styles import Style
import asyncio
from typing import Any

class EDSMState(module.ModuleState): # All variables in this class persist between program runs. 
    events_buffer: list[str] = []


class EDSM(module.Module): 
    style = Style.from_dict({   # The KeyValue-s in this dictionary can be accessed as html tag modifiers in self.print
        "module_color": "#5bc0de",              # Example: self.print(f"<module_color>Hello World.</module_color>")
    })

    MODULE_NAME: str = "ExampleModule"
    MODULE_VERSION: str = "?"
    STATE_TYPE = ExampleModuleState     # If your module has its own state class, then this has to be set to it. 
    state: ExampleModuleState = ExampleModuleState() # pyright: ignore[reportIncompatibleVariableOverride]
    responses: list[int] = []

    def __init__(self) -> None:
        super().__init__()

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:   # Events are either new journal file lines or events produced by EDSST
        await super().process_event(event, tg)
        match event["event"]:   # Events are currently passed as dict[str, Any]
            case "FSDJump": 
                self.print(f"<module_color>Enjoy the Ride!</module_color>") # It is recommended to always use self.print
            case _: pass

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        await super().process_user_input(arguments, tg)
        if arguments[0] in ["examplemodule", "examplesurvey", "example"]:   # Currently this is the way to define extra aliases for your module
            match arguments[1]:
                case "echo":
                    if len(arguments) < 2: return
                    self.state.example_state_entry = " ".join(iter(str(arguments[2:])))
                    self.print(f"{self.state.example_state_entry}", prefix="<module_color>echo</module_color>: ")
                case _: pass