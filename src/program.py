from abc import ABC
from typing import Any
from pathlib import Path
from cli_color_py import bright_blue, bright_cyan, bright_green, yellow # pyright: ignore[reportMissingTypeStubs]
    ##black, red, green, yellow, blue, magenta, cyan, white, bright_red, bright_green, bright_yellow, bright_blue, bright_magenta, bright_cyan
from src.util import text_to_clipboard
import json

from src.util import read_file_by_lines, reserialize_file

class Program(ABC):
    SURVEY_DIR: Path
    STATE_FILE_PATH: Path
    active: bool

    def __init__(self):
        ...
    def save_state(self):
        ...
    def load_state(self):
        ...
    def process_initial_event(self, event: Any):
        ...
    def process_event(self, event: Any) -> None:
        ...

class CoreProgram(Program):
    SURVEY_DIR = Path("surveys/core")
    STATE_FILE_PATH = SURVEY_DIR / Path("core_survey_state")
    active = True
    commander_greeted = False
    current_system: str = ""
    terraformables: list[str] = []
    biologicals: list[tuple[str, int]] = []
    geologicals: list[tuple[str, int]] = []
    total_bio_signatures: int = 0
    total_geo_signatures: int = 0

    # TODO: If player scans stuff while the survey or program is crashed but restarts the survey or program before finishing the scan, 
    #       then the results are not necessarily synced

    def __init__(self) -> None:
        if not self.SURVEY_DIR.exists():
            self.SURVEY_DIR.mkdir()
        self.load_state()
        self.save_state()


    def save_state(self) -> None:
        state: dict[str, Any] = {
                "active": self.active,
                "current_system": self.current_system,
                "terraformables": self.terraformables,
                "biologicals": self.biologicals,
                "geologicals": self.geologicals,
                "total_bio_signatures": self.total_bio_signatures,
                "total_geo_signatures": self.total_geo_signatures,
            }
        json.dump(state, self.STATE_FILE_PATH.open("w"))

    def load_state(self):
        if self.STATE_FILE_PATH.exists():
            state = json.load(self.STATE_FILE_PATH.open())
            self.active = True
            self.current_system = state["current_system"]
            self.terraformables = state["terraformables"]
            self.biologicals = state["biologicals"]
            self.geologicals = state["geologicals"]
            self.total_bio_signatures = state["total_bio_signatures"]
            self.total_geo_signatures = state["total_geo_signatures"]

    def process_initial_event(self, event: Any) -> None:
        match event["event"]:
            case "Commander":
                if not self.commander_greeted:
                    print("Welcome, Commander " + event["Name"])
                    self.commander_greeted = True
            case "Shutdown":
                print("Elite: Dangerous not launched!\nExiting.")
                exit()
            case _: pass

    def process_event(self, event: Any) -> None:
        match event["event"]:
            case "Shutdown":
                exit("Elite Stellar Survey Tools spooling down...\nFarewell, Commander!")
            case "FSSBodySignals":
                for signal in event["Signals"]:
                    match signal["Type"]:
                        case "$SAA_SignalType_Biological;":
                            biological = (str(event["BodyName"]), int(signal["Count"]))
                            self.biologicals.append(biological)
                            self.total_bio_signatures += int(signal["Count"])
                            self.save_state()
                        case "$SAA_SignalType_Geological;":
                            geological = (str(event["BodyName"]), int(signal["Count"]))
                            self.geologicals.append(geological)
                            self.total_geo_signatures += int(signal["Count"])
                            self.save_state()
                        case _: pass
            case "Scan":
                if "TerraformState" in event:
                    if event["TerraformState"] == "Terraformable":
                        self.terraformables.append(event["BodyName"])
                        self.save_state()
            case "FSSAllBodiesFound":
                print(bright_cyan("\nFull system scan complete!\n"))
                if self.terraformables:
                    print(bright_blue("Terraformable planets: " + str(len(self.terraformables))))
                    for terraformable in self.terraformables:
                        print(bright_blue("\t" + terraformable))
                if self.biologicals:
                    print(bright_green("Biological signatures: " + str(len(self.biologicals)) + " (" + str(self.total_bio_signatures) + ")"))
                    for biological in self.biologicals:
                        print(bright_green("\t" + biological[0] + ": " + str(biological[1])))
                if self.geologicals:
                    print(yellow("Geological signatures: " + str(len(self.geologicals)) + " (" + str(self.total_geo_signatures) + ")"))
                    for geological in self.geologicals:
                        print(yellow("\t" + geological[0] + ": " + str(geological[1])))
            case "StartJump":
                self.terraformables = []
                self.biologicals = []
                self.geologicals = []
                self.total_bio_signatures = 0
                self.total_geo_signatures = 0
                self.save_state()
            case "FSDJump":
                self.current_system = event["StarSystem"]
                self.save_state()
                print("Jumped to system: " + self.current_system)
            case _: pass

class BoxelSurvey(Program):
    SURVEY_DIR = Path("surveys/BoxelSurvey")
    BOXEL_LOG_FILE_PATH: Path = SURVEY_DIR / Path("boxel_log")
    SYSTEM_LIST_FILE_PATH: Path = SURVEY_DIR / Path("boxel_survey_system_list")
    STATE_FILE_PATH = SURVEY_DIR / Path("boxel_survey_state")
    active = False
    system_list: list[str]
    next_system: str
    core_program: Program

    def __init__(self, core_program: Program) -> None:
        if not self.SURVEY_DIR.exists():
            self.SURVEY_DIR.mkdir()
        self.core_program = core_program
        self.load_state()
        self.save_state()
        if self.active:
            self.system_list = read_file_by_lines(self.SYSTEM_LIST_FILE_PATH)
            self.next_system = self.load_next_system()
            if self.next_system:
                text_to_clipboard(self.next_system)
                print("Ongoing Boxel survey\nNext Boxel survey system: " + self.next_system)
            else:
                print("No systems in systemlist for scanning!\nPlease populate systemlist file and try again.")
                self.active = False
                self.save_state()

    def save_state(self) -> None:
        state: dict[str, Any] = {"active":self.active}
        json.dump(state, self.STATE_FILE_PATH.open("w"))

    def load_state(self) -> None:
        if self.STATE_FILE_PATH.exists():
            state = json.load(self.STATE_FILE_PATH.open())
            self.active = state["active"]
    
    def process_event(self, event: Any) -> None:
        match event["event"]:
            case "FSDJump":
                if self.next_system.lower() == event["StarSystem"].lower():
                    reserialize_file(self.SYSTEM_LIST_FILE_PATH, self.system_list)
                    open(self.BOXEL_LOG_FILE_PATH, "a").write(self.next_system + "\n")
                    if not self.system_list:
                        print("Boxel Survey Completed!")
                        self.active = False
                        self.save_state()
                        return
                    self.next_system = self.load_next_system()
                    text_to_clipboard(self.next_system)
                    print("Next Boxel Survey System: ", self.next_system)
            case _: pass

    def load_next_system(self) -> str:
        return self.system_list.pop(0)

class DensityColumnSurvey(Program):
    SURVEY_DIR = Path("surveys/DensityColumnSurvey")
    STATE_FILE_PATH = SURVEY_DIR / Path("density_column_survey_state")
    active = False

    def __init__(self) -> None:
        if not self.SURVEY_DIR.exists():
            self.SURVEY_DIR.mkdir()
        self.load_state()
        self.save_state()
    
    def save_state(self) -> None:
        state: dict[str, Any] = {"active":self.active}
        json.dump(state, self.STATE_FILE_PATH.open("w"))
    
    def load_state(self) -> None:
        if self.STATE_FILE_PATH.exists():
            state = json.load(self.STATE_FILE_PATH.open())
            self.active = state["active"]

    def process_event(self, event: Any) -> None:
        match event["event"]:
            case "FSDJump":
                coordinates_and_system = f'{event["StarPos"][0]}\t{event["StarPos"][1]}\t{event["StarPos"][2]}\t{event["StarSystem"]}'
                text_to_clipboard(coordinates_and_system)
            case _: pass

class DensityNavRouteSurvey(Program):
    pass

