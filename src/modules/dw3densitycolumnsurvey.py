from src.modules.core import CoreModule
from src.modules.module import Module, ModuleState
from src.util import read_file_by_lines, reserialize_file
from prompt_toolkit.styles import Style
import asyncio
import math
from pathlib import Path
from typing import Any

class DW3DensityColumnSuveyState(ModuleState):
    MAX_HEIGHT_DEVIATION: float = 10
    system_in_sequence: int = 0
    start_height: int = 0
    direction: int = 0
    previous_system: str = ""
    valid_system: bool = False
    system_surveyed: bool = False
    survey_ongoing: bool = False
    survey_start_system: str = ""

class DW3DensityColumnSurvey(Module):
    style = Style.from_dict({
        "module_color": "#ff00ff",
    })

    MODULE_NAME = "DW3DensityColumnSurvey"
    MODULE_VERSION: str = "0.0.3"
    EXTRA_ALIASES: set[str] = set(["dcs", "dc", "dw3c", "column", "densitycolumn", "densitycolumnsurvey", "dw3densitycolumnsurvey"])
    survey_data_dir: Path = Path("")
    survey_file_path: Path = Path("")
    STATE_TYPE = DW3DensityColumnSuveyState
    core: CoreModule
    state: DW3DensityColumnSuveyState = DW3DensityColumnSuveyState()

    def __init__(self, core: CoreModule) -> None:
        super().__init__(self.EXTRA_ALIASES)
        self.survey_data_dir = Path(self.module_dir / "surveyed_columns")
        if not self.survey_data_dir.exists():
            self.survey_data_dir.mkdir()
        if self.state.survey_start_system:
            self.survey_file_path = Path(self.survey_data_dir / f"{self.state.survey_start_system}")
        else:
            self.survey_file_path = Path(self.module_dir / "default.tsv")
        if not self.survey_file_path.exists():
            self.survey_file_path.open("w")
        self.save_state()
        self.core = core

    async def process_event(self, event: Any, event_raw: str, tg: asyncio.TaskGroup) -> None:
        await super().process_event(event, event_raw,  tg)
        if self.state.survey_ongoing:
            match event["event"]:
                case "FSDJump":
                    current_height = self.core.state.current_system.coordinates[1]
                    if abs(current_height - self.get_expected_galactic_height()) < self.state.MAX_HEIGHT_DEVIATION:
                        self.state.valid_system = True
                        self.print("System valid for survey!")
                case "CaughtUp":
                    self.caught_up = True
                    if self.state.system_in_sequence > 0:
                        self.print(f"Density column survey ongoing! Direction: <cyan>{"up" if self.state.direction == 1 else "down"}</cyan>, Last system: <green>{self.state.previous_system}</green>")
                case _: pass
        else: pass

    def is_valid_starting_height(self, galactic_height: float, direction: str) -> bool:
        return True if (abs(galactic_height - 1000) < self.state.MAX_HEIGHT_DEVIATION and direction == "down") or \
                (abs(galactic_height + 1000) < self.state.MAX_HEIGHT_DEVIATION and direction == "up") or \
                (abs(galactic_height) < self.state.MAX_HEIGHT_DEVIATION ) else False

    def get_expected_galactic_height(self) -> float:
        return self.state.start_height + 50 * self.state.direction * self.state.system_in_sequence

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        await super().process_user_input(arguments, tg)

        # TODO: Refactor this mess

        if len(arguments) > 1:
            if self.state.enabled and self.caught_up:
                galactic_height = self.core.state.current_system.coordinates[1]
                count = 0
                distance = 0.0
                match arguments[1]:
                    case "start" | "begin":
                        if len(arguments) < 3:
                            self.print("<error>Direction parameter required to start survey!</error>")
                            return
                        if arguments[2] not in ["up", "ascending", "down", "descending", "-1", "1", "+1"]:
                            self.print("<error>Invalid direction parameter - Must be 'up', 'ascending', 'down', or 'descending'!</error>")
                            return
                        if self.is_valid_starting_height(galactic_height, arguments[2]):
                            self.state.direction = 1 if arguments[2] in ["up", "ascending"] else -1
                            self.state.valid_system = True
                            self.state.start_height = -1000 if galactic_height < -500 else 0 if galactic_height < 500 else 1000
                            self.state.system_in_sequence = 0
                            self.state.survey_ongoing = True
                            self.state.survey_start_system = self.core.state.current_system.name
                            self.survey_file_path = Path(self.survey_data_dir / str(self.core.state.current_system.name + ".tsv"))
                            self.survey_file_path.open("w")
                            self.print("<module_color>Started Density Column Survey from system: </module_color>" + self.core.state.current_system.name)
                            self.print("Please make sure to enter current system's count and max distance before continuing!")
                            return
                        else:
                            self.print("<error>Will not start the survey - Too far from a valid startpoint!</error>")
                            self.print("Please move to a galactic height of -1000, 0, or 1000 +-" + str(self.state.MAX_HEIGHT_DEVIATION) + "Ly and try again!")
                            return

                    case "undo":
                        survey = read_file_by_lines(self.survey_file_path)
                        if len(survey) > 0:
                            removed = survey.pop(0).split(sep="\t")
                            self.print(f"Removed datapoint for system: {removed[0]}")
                        else:
                            self.print("No datapoints to remove!")
                            return
                        reserialize_file(self.survey_file_path, survey)
                        self.state.system_in_sequence -= 1
                        self.state.previous_system = "UNKNOWN"
                        self.state.system_surveyed = False
                        await self.process_event({"event":"FSDJump"}, "{\"event\": \"FSDJump\"}", tg)
                        self.save_state()

                    case "reset" | "clear":
                        self.survey_file_path.unlink(missing_ok=True)
                        self.survey_file_path = Path(self.module_dir / "default.tsv")
                        self.state.system_in_sequence = 0
                        self.state.previous_system = ""
                        self.state.valid_system = False
                        self.state.system_surveyed = False
                        self.state.start_height = 0
                        self.state.direction = 0
                        self.state.survey_ongoing = False
                        self.state.survey_start_system = ""
                        self.print("Cleared current survey progress.")
                        self.save_state()
                        return

                    case _:
                        if self.state.survey_ongoing:
                            try:
                                count = abs(int(arguments[1]))
                                if count > 49:
                                    self.print("<error>Count value cannot exceed 49!</error>\n" +
                                    "Make sure you counted the number of neighboring systems in the nav panel correctly" +
                                    " and make sure no FSD route is planned.")
                                    return
                            except ValueError:
                                self.print("<error>Received invalid count value: </error>" + arguments[1])
                                return
                            if len(arguments) < 3:
                                self.print("<error>Missing distance value!</error>")
                                return
                            try:
                                distance = abs(float(arguments[2]))
                                if distance > 20:
                                    self.print("<error>Distance value cannot exceed 20!</error>\n" +
                                    "Make sure you read the distance to the furthest system correctly and make sure no FSD route is planned.")
                                    return
                            except ValueError:
                                self.print("<error>Received invalid distance value: </error>" + arguments[2])
                                return
                            self.process_datapoint(count, distance)
                        else:
                            self.print("No ongoing survey - Please start a survey first!")
                            return

    def process_datapoint(self, count: int, distance: float) -> None:
        current_height = self.core.state.current_system.coordinates[1]
        if not self.state.valid_system:
            self.print("<error>Current system is not valid for survey - Height deviation too large!</error>")
            self.print("Current galactic height: <error>" +
                    str(current_height) +
                    "Ly</error>, expected <error>" +
                    str(self.get_expected_galactic_height()) +
                    "Ly.</error>")
            return
        rho: float = 50 / ((4/3) * math.pi * (distance ** 3)) if count + 1 == 50 else (count + 1) / ((4/3) * math.pi * 8000)
        #Rho is calculated based on the direct translation of the formula in the DW3 Stellar Density Scan Worksheet spreadsheet: 
        # =IFS(D6=50,50/((4*PI()/3)*(E6^3)),D6<50,D6/((4*pi()/3)*(20^3)))
        datapoint: str = f"""{self.core.state.current_system.name}\t\
{self.get_expected_galactic_height()}\t\
{count}\t\
{count + 1}\t\
{distance}\t\
{rho}\t\
{self.core.state.current_system.coordinates[0]}\t\
{self.core.state.current_system.coordinates[1]}\t\
{self.core.state.current_system.coordinates[2]}"""
        if self.state.direction == 1:
            open(self.survey_file_path, "a").write(datapoint)
        else:
            data: list[str] = []
            data.append(datapoint)
            for line in self.survey_file_path.open().readlines():
                data.append(line)
            reserialize_file(self.survey_file_path, data)
        self.print(f"<module_color>Recorded datapoint for system: </module_color>{self.core.state.current_system.name}")
        self.print(f"{datapoint}\n", prefix="")
        self.state.system_in_sequence += 1
        self.state.previous_system = self.core.state.current_system.name
        self.state.system_surveyed = True
        self.state.valid_system = False
        self.save_state()
        if self.state.system_in_sequence == 20:
            self.print("<module_color>Survey completed!</module_color>\n")
            self.state.system_in_sequence = 0
            self.state.previous_system = ""
            self.state.system_surveyed = False
            self.state.survey_start_system = ""
            self.save_state()
            return