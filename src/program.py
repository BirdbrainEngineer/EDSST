from abc import ABC
from typing import Any
from pathlib import Path
from cli_color_py import bright_blue, bright_cyan, bright_green, yellow # pyright: ignore[reportMissingTypeStubs]
    ##black, red, green, yellow, blue, magenta, cyan, white, bright_red, bright_green, bright_yellow, bright_blue, bright_magenta, bright_cyan
from src.util import text_to_clipboard
import json

SYSTEM_LIST_FILE = Path("data/systemlist")
BOXEL_LOG_FILE = Path("data/boxel_log")

def read_system_list() -> list[str]:
    with open(SYSTEM_LIST_FILE) as f:
        return f.read().split("\n")
    
def reserialize_file(path: Path, contents: list[str]) -> None:
    open(path, "w").write("\n".join(contents))

def load_next_system(system_list: list[str]) -> str:
    return system_list.pop(0)


class Program(ABC):
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
    STATE_PATH: Path = Path("state/CoreProgram")
    active = True
    commander_greeted = False
    current_system: str = ""
    terraformables: list[str] = []
    biologicals: list[tuple[str, int]] = []
    geologicals: list[tuple[str, int]] = []
    total_bio_signatures: int = 0
    total_geo_signatures: int = 0

    # TODO: add save and load state

    def __init__(self) -> None:
        pass

    def save_state(self) -> None:
        pass

    def load_state(self):
        if self.STATE_PATH.exists():
            state = json.load(self.STATE_PATH.open())
            self.active = state["active"]

    def process_initial_event(self, event: Any) -> None:
        match event["event"]:
            case "Commander":
                if not self.commander_greeted:
                    print("Welcome Commander " + event["Name"])
                    self.commander_greeted = True
            case "Shutdown":
                print("Elite: Dangerous not launched!\nExiting.")
                exit()
            case _: pass

    def process_event(self, event: Any) -> None:
        match event["event"]:
            case "Shutdown":
                exit()
            case "FSSBodySignals":
                for signal in event["Signals"]:
                    match signal["Type"]:
                        case "$SAA_SignalType_Biological;":
                            biological = (str(event["BodyName"]), int(signal["Count"]))
                            self.biologicals.append(biological)
                            self.total_bio_signatures += int(signal["Count"])
                        case "$SAA_SignalType_Geological;":
                            geological = (str(event["BodyName"]), int(signal["Count"]))
                            self.geologicals.append(geological)
                            self.total_geo_signatures += int(signal["Count"])
                        case _: pass
            case "Scan":
                if "TerraformState" in event:
                    if event["TerraformState"] == "Terraformable":
                        self.terraformables.append(event["BodyName"])
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
            case "FSDJump":
                print("Jumped to system:", event["StarSystem"])
            case _: pass

class BoxelSurvey(Program):
    STATE_PATH: Path = Path("state/BoxelSurvey.json")
    active = False
    system_list: list[str]
    next_system: str

    def __init__(self) -> None:
        self.load_state()
        self.save_state()
        if self.active:
            self.system_list = read_system_list()
            self.next_system = load_next_system(self.system_list)
            if self.next_system:
                text_to_clipboard(self.next_system)
                print("Ongoing Boxel survey\nNext Boxel survey system: " + self.next_system)
            else:
                print("No systems in systemlist for scanning!\nPlease populate systemlist file and try again.")
                self.active = False
                self.save_state()

    def save_state(self) -> None:
        state = {"active":self.active}
        json.dump(state, self.STATE_PATH.open("w"))

    def load_state(self) -> None:
        if self.STATE_PATH.exists():
            state = json.load(self.STATE_PATH.open())
            self.active = state["active"]
    
    def process_event(self, event: Any) -> None:
        match event["event"]:
            case "FSDJump":
                if self.next_system.lower() == event["StarSystem"].lower() and self.active:
                    reserialize_file(SYSTEM_LIST_FILE, self.system_list)
                    open(BOXEL_LOG_FILE, "a").write(self.next_system + "\n")
                    if not self.system_list:
                        print("Boxel Survey Completed!")
                        self.active = False
                        self.save_state()
                        return
                    self.next_system = load_next_system(self.system_list)
                    text_to_clipboard(self.next_system)
                    print("Next Boxel Survey System: ", self.next_system)
            case _: pass

class DensityColumnSurvey(Program):
    STATE_PATH: Path = Path("state/DensityColumnSurvey.json")
    active = False

    def __init__(self) -> None:
        self.load_state()
        self.save_state()
    
    def save_state(self) -> None:
        state = {"active":self.active}
        json.dump(state, self.STATE_PATH.open("w"))
    
    def load_state(self) -> None:
        if self.STATE_PATH.exists():
            state = json.load(self.STATE_PATH.open())
            self.active = state["active"]

    def process_event(self, event: Any) -> None:
        match event["event"]:
            case "FSDJump":
                coordinates_and_system = f'{event["StarPos"][0]}\t{event["StarPos"][1]}\t{event["StarPos"][2]}\t{event["StarSystem"]}'
                text_to_clipboard(coordinates_and_system)
            case _: pass

class DensityNavRouteSurvey(Program):
    pass

