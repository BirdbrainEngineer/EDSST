from src.modules import module
from prompt_toolkit.styles import Style
import asyncio
from typing import Any

class ExampleModuleState(module.ModuleState): # All variables in this class persist between program runs. 
    # enabled: bool     Inherited enabled state flag. Don't override unless you know what you are doing...
    example_state_entry: str = ""


class ExampleModule(module.Module): 
    style = Style.from_dict({   # The KeyValue-s in this dictionary can be accessed as html tag modifiers in self.print
        "module_color": "#00ff00",              # Example: self.print(f"<module_color>Hello World.</module_color>")
    })
    # ------------ Inherited variables ------------
    #module_dir: Path           Path to the module data directory. This should not be changed unless you know what you are doing...
    #state_file_path: Path      Path to the module state file in the module data directory. This should not be changed unless you know what you are doing...
    #caught_up: bool            flag to know whether the program has processed all the previous lines in the latest journal
    # ------------ Situationally required variables ------------
    EXTRA_ALIASES: set[str] = set(["moduleAlias", "moduleextraalias", "ThirdAlias"])  # Aliases are case insensitive.
    STATE_TYPE = ExampleModuleState     # If your module has its own state class, then this has to be set to it. 
    state: ExampleModuleState = ExampleModuleState()    # If your module has its own state class, then it has to be initialized here. # pyright: ignore[reportIncompatibleVariableOverride]
    # ------------ Required variables ------------
    MODULE_NAME: str = "ExampleModule"
    MODULE_VERSION: str = "?"

    def __init__(self) -> None:
        super().__init__(self.EXTRA_ALIASES) # It is *highly* recommended to call 'super().__init__(self.EXTRA_ALIASES)' before your own initialization code. 

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:   # Events are either new journal file lines or events produced by EDSST
        await super().process_event(event, tg)
        match event["event"]:   # Events are currently passed as dict[str, Any]
            case "FSDJump": 
                self.print(f"<module_color>Enjoy the Ride!</module_color>") # It is recommended to always use self.print
            case _: pass

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        await super().process_user_input(arguments, tg)
        match arguments[1]:
            case "echo":
                if len(arguments) < 2: return
                self.state.example_state_entry = " ".join(iter(str(arguments[2:])))
                self.print(f"{self.state.example_state_entry}", prefix="<module_color>echo</module_color>: ")
            case _: pass