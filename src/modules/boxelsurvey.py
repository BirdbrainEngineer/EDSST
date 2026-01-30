from src.modules.module import Module
from src.util import reserialize_file, text_to_clipboard
from prompt_toolkit.styles import Style
import asyncio
import json
from pathlib import Path
from typing import Any


class BoxelSurvey(Module):
    style = Style.from_dict({
        "module_color": "#ffff00",
    })

    MODULE_NAME = "BoxelSurvey"
    MODULE_VERSION: str = "0.0.1"
    boxel_log_file_path: Path
    system_list_file_path: Path
    system_list: list[str]
    next_system: str = ""
    core: Module

    def __init__(self, core: Module) -> None:
        super().__init__()
        self.boxel_log_file_path = self.module_dir / Path("boxel_log")
        self.system_list_file_path = self.module_dir / Path("boxel_survey_system_list")
        self.core = core

    async def process_event(self, event: Any, event_raw: str, tg: asyncio.TaskGroup) -> None:
        await super().process_event(event, event_raw, tg)
        match event["event"]:
            case "FSDJump":
                if self.next_system.lower() == event["StarSystem"].lower():
                    reserialize_file(self.system_list_file_path, self.system_list)
                    open(self.boxel_log_file_path, "a").write(self.next_system + "\n")
                    if not self.system_list:
                        self.print(" <survey_color>Survey Completed!</survey_color> ")
                        self.disable()
                        self.save_state()
                        return
                    self.next_system = self.load_next_system()
                    text_to_clipboard(self.next_system)
                    self.print("Next system: " + self.next_system)
            case _: pass

    def load_next_system(self) -> str:
        return self.system_list.pop(0)

    def save_state(self) -> None:
        state: dict[str, Any] = {"enabled":self.state.enabled, "version":self.MODULE_VERSION}
        json.dump(state, self.state_file_path.open("w"))

    def load_state(self) -> None:
        if self.state_file_path.exists():
            state = json.load(self.state_file_path.open())
            self.enabled = state["enabled"]