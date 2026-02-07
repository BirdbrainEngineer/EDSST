from src.modules import module, edsm, core
from src.util import text_to_clipboard
from prompt_toolkit.styles import Style
import asyncio
from pathlib import Path
from typing import Any
from src.version import TESTING_MODE, TestingMode

class BoxelSurveyState(module.ModuleState):
    system_list: list[str] = []
    ignore_systems_set: set[str] = set()
    systems_to_survey: int = 0
    systems_in_boxel: int = 0
    boxel_name: str = ""
    next_system: str = ""
    survey_ongoing: bool = False

class BoxelSurvey(module.Module):
    style = Style.from_dict({
        "module_color": "#ffff00",
    })

    MODULE_NAME = "BoxelSurvey"
    MODULE_VERSION: str = "0.1.2"
    EXTRA_ALIASES: set[str] = set(["boxel", "boxels"])
    STATE_TYPE = BoxelSurveyState
    boxel_log_file_path: Path
    core: core.CoreModule
    edsm: edsm.EDSM
    state: BoxelSurveyState = BoxelSurveyState()

    def __init__(self, core: core.CoreModule, edsm: edsm.EDSM) -> None:
        super().__init__(self.EXTRA_ALIASES)
        self.boxel_log_file_path = self.module_dir / Path("boxel_log")
        self.core = core
        self.edsm = edsm

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:
        await super().process_event(event, tg)
        match event["event"]:
            case "FSDJump":
                if self.state.survey_ongoing:
                    self.update_survey(str(event["StarSystem"]))
            case "CaughtUp":
                if self.state.survey_ongoing:
                    self.print(f"Boxel survey ongoing! Next system: <cyan>{self.state.next_system}</cyan>")
                    text_to_clipboard(self.state.next_system)
            case _: pass

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        await super().process_user_input(arguments, tg)
        if not self.caught_up or not self.state.enabled:
            return
        match arguments[1]:
            case "status" | "state":
                if self.state.survey_ongoing:
                    self.print(f"Systems left to scan: {len(self.state.system_list) - len(self.state.ignore_systems_set)}")
                    self.print(f"Next system: <cyan>{self.state.next_system}</cyan>")
                    
                    if TESTING_MODE == TestingMode.Testing:
                        self.print("Systems visited by others:")
                        self.print(f"{"\n".join(self.state.ignore_systems_set)}", prefix="")
                else:
                    self.print("No survey ongoing!")

            case "show" | "log":
                if not self.state.survey_ongoing:
                    self.print("No survey ongoing!")
                else:
                    self.print("Systems left in queue:")
                    self.print(f"{"\n".join(self.state.system_list)}", prefix="")

            case "skip":
                self.skip_system()

            case "copy":
                text_to_clipboard(self.state.next_system)

            case "survey":
                # boxel survey [num_to_scan] of [num_of_stars] in [boxel_name]
                if self.state.survey_ongoing:
                    self.print("Survey already ongoing!")
                    return
                if len(arguments) < 7:
                    self.print("<error>Missing arguments!</error>")
                    self.print("Expression must have the following form:")
                    self.print("survey <red>[num_to_scan]</red> of <green>[num_of_stars]</green> in <bright_blue>[boxel_name]</bright_blue>")
                    return
                if arguments[2] in ("all", "a"):
                    try:
                        self.state.systems_to_survey = int(arguments[4])
                    except ValueError:
                        self.print("<error>Need an integer on argument for how many systems are in the boxel!</error>")
                        self.clear_survey()
                        return
                else:
                    try:
                        self.state.systems_to_survey = int(arguments[2])
                    except ValueError:
                        self.print("<error>Need an integer on argument for how many systems to survey!</error>")
                        self.clear_survey()
                        return
                if self.state.systems_to_survey < 1:
                    self.print("<error>Need to survey at least one system!</error>")
                    self.clear_survey()
                    return
                if arguments[3] == "of": 
                    try:
                        self.state.systems_in_boxel = int(arguments[4])
                    except ValueError:
                        self.print("<error>Need an integer on argument for how many systems are in the boxel!</error>")
                        return
                    if self.state.systems_in_boxel < self.state.systems_to_survey:
                        self.print("Can't survey more systems than exists in the boxel!")
                        self.clear_survey()
                        return
                    if arguments[5] in ("in", "from"):
                        self.state.boxel_name = " ".join(arguments[6:])
                        for i in range(self.state.systems_to_survey):
                            system_number = int(i*((self.state.systems_in_boxel-1)/(self.state.systems_to_survey-1)))
                            self.state.system_list.append(f"{self.state.boxel_name}{system_number}")
                        response: Any | None = await self.edsm.get_systems(self.state.system_list)
                        if response:
                            for system in response:
                                self.state.ignore_systems_set.add(str(system["name"]).lower())
                        self.state.survey_ongoing = True
                        self.state.next_system = self.state.system_list[0]
                        if self.state.next_system in self.state.ignore_systems_set or self.state.next_system == self.core.state.current_system.name.lower():
                            self.update_survey(self.state.next_system)
                        else:
                            text_to_clipboard(self.state.next_system)
                            self.print(f"Next system: <cyan>{self.state.next_system}</cyan>")
                        return
                self.print("<error>Malformed survey start expression!</error>")
                self.print("Expression must have the following form:")
                self.print("survey <red>[num_to_scan]</red> of <green>[num_of_stars]</green> in <bright_blue>[boxel_name]</bright_blue>")

            case "clear" | "finish":
                if self.state.survey_ongoing:
                    self.print("<red>Survey cleared!</red>")
                    self.print("Be aware that the information about the total number of systems in the boxel will be lost if not manually recorded!")
                    self.clear_survey()
                else:
                    self.print("No survey ongoing!")
            case _: pass

    def skip_system(self) -> None:
        self.print(f"Skipping system {self.state.next_system}.")
        if len(self.state.system_list) > 0:
            self.state.next_system = self.load_next_system()
            while self.state.next_system in self.state.ignore_systems_set:
                open(self.boxel_log_file_path, "a").write(self.state.next_system + "\n")
                self.state.ignore_systems_set.remove(self.state.next_system)
                self.print(f"System <cyan>{self.state.next_system}</cyan> has already been visited by someone... Skipping.")
                if not self.state.system_list:
                    break
                self.state.next_system = self.load_next_system()
            text_to_clipboard(self.state.next_system)
            self.print(f"Next system: <cyan>{self.state.next_system}</cyan>")
            self.save_state()
        else:
            self.print("<green>Survey Completed!</green>")
            self.clear_survey()

    def update_survey(self, star_system: str) -> None:
        if self.state.next_system.lower() == star_system.lower().strip():
            self.print(f"Updating survey with system <cyan>{star_system}</cyan>")
            open(self.boxel_log_file_path, "a").write(self.state.next_system + "\n")
            if len(self.state.system_list) > 0:
                self.state.next_system = self.load_next_system()
                while self.state.next_system in self.state.ignore_systems_set:
                    open(self.boxel_log_file_path, "a").write(self.state.next_system + "\n")
                    self.state.ignore_systems_set.remove(self.state.next_system)
                    self.print(f"System <cyan>{self.state.next_system}</cyan> has already been visited by someone... Skipping.")
                    if not self.state.system_list:
                        break
                    self.state.next_system = self.load_next_system()
                text_to_clipboard(self.state.next_system)
                self.print(f"Next system: <cyan>{self.state.next_system}</cyan>")
                self.save_state()
            else:
                self.print("<green>Survey Completed!</green>")
                self.clear_survey()

    def load_next_system(self) -> str:
        return self.state.system_list.pop(0)
    
    def clear_survey(self) -> None:
        self.state.next_system = ""
        self.state.systems_to_survey = 0
        self.state.systems_in_boxel = 0
        self.state.boxel_name = ""
        self.state.survey_ongoing = False
        self.state.system_list.clear()
        self.state.ignore_systems_set.clear()
        self.save_state()