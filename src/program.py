from collections import defaultdict
from typing import Any
from pathlib import Path
from cli_color_py import bright_blue, bright_cyan, bright_green, yellow # pyright: ignore[reportMissingTypeStubs]
    ##black, red, green, yellow, blue, magenta, cyan, white, bright_red, bright_green, bright_yellow, bright_blue, bright_magenta, bright_cyan
from src.util import text_to_clipboard, get_distance, reserialize_file
import json

class Program():
    SURVEY_NAME: str = "unnamed_survey"
    survey_dir: Path
    state_file_path: Path
    active: bool = False

    def __init__(self) -> None:
        print("ESST: Loading module: " + self.SURVEY_NAME)
        self.survey_dir = Path("surveys") / Path(self.SURVEY_NAME)
        self.state_file_path = self.survey_dir / Path(self.SURVEY_NAME + "_state")
        if not self.survey_dir.exists():
            self.survey_dir.mkdir()
        self.load_state()
        self.save_state()

    def enable(self) -> None:
        self.active = True
        self.save_state()
        print("ESST: " + self.SURVEY_NAME + " enabled!")

    def disable(self) -> None:
        self.active = False
        self.save_state()
        print("ESST: " + self.SURVEY_NAME + " disabled!")

    def save_state(self) -> None:
        state: dict[str, Any] = {"active":self.active}
        json.dump(state, self.state_file_path.open("w"))

    def load_state(self) -> None:
        if self.state_file_path.exists():
            state = json.load(self.state_file_path.open())
            self.active = state["active"]

    def process_past_event(self, event: Any) -> None:
        pass

    def process_event(self, event: Any) -> None:
        pass

class CoreProgram(Program):
    SURVEY_NAME = "core"
    active = True
    commander_greeted = False
    current_system: str = ""
    system_coordinates: tuple[float, float, float] = (0.0, 0.0, 0.0)
    system_address: int = 0
    bodies: dict[int, dict[str, Any]] = defaultdict(dict)
    clusters:                   set[int] = set()
    stars:                      set[int] = set()
    icy_bodies:                 set[int] = set()
    rocky_icy_bodies:           set[int] = set()
    rocky_bodies:               set[int] = set()
    metal_rich_bodies:          set[int] = set()
    high_metal_content_bodies:  set[int] = set()
    earth_like_world_bodies:    set[int] = set()
    ammonia_world_bodies:       set[int] = set()
    water_world_bodies:         set[int] = set()
    gas_giant_bodies:           set[int] = set()
    landables:                  set[int] = set()
    atmospherics:               set[int] = set()
    ringed:                     set[int] = set()
    terraformables:             set[int] = set()
    volcanisms:                 set[int] = set()
    biologicals:                set[int] = set()
    geologicals:                set[int] = set()
    guardians:                  set[int] = set()
    thargoids:                  set[int] = set()    

    # TODO: If player scans stuff while the survey or program is not open but starts or restarts the survey or program before finishing the scan, 
    #       then the results are not necessarily synced  
    # TODO: Spansh and/or EDSM integration.

    def enable(self) -> None:
        self.active = True
        self.save_state()
        print("ESST: Core module is always enabled!")

    def disable(self) -> None:
        self.active = True
        self.save_state()
        print("ESST: Core module cannot be disabled!")

    def save_state(self) -> None:
        state: dict[str, Any] = {
                "active":                       self.active,
                "current_system":               self.current_system,
                "system_coordinates":           self.system_coordinates,
                "system_address":               self.system_address,
                "bodies":                       self.bodies,
                "stars":                        self.stars,
                "clusters":                     self.clusters,
                "icy_bodies":                   self.icy_bodies,
                "rocky_icy_bodies":             self.rocky_icy_bodies,
                "rocky_bodies":                 self.rocky_bodies,
                "metal_rich_bodies":            self.metal_rich_bodies,
                "high_metal_content_bodies":    self.high_metal_content_bodies,
                "earth_like_world_bodies":      self.earth_like_world_bodies,
                "ammonia_world_bodies":         self.ammonia_world_bodies,
                "water_world_bodies":           self.water_world_bodies,
                "gas_giant_bodies":             self.gas_giant_bodies,
                "landables":                    self.landables,
                "atmospherics":                 self.atmospherics,
                "ringed":                       self.ringed,
                "volcanisms":                   self.volcanisms,
                "terraformables":               self.terraformables,
                "biologicals":                  self.biologicals,
                "geologicals":                  self.geologicals,
                "guardians":                    self.guardians,
                "thargoids":                    self.thargoids,
            }
        json.dump(state, self.state_file_path.open("w"))

    def load_state(self):
        if self.state_file_path.exists():
            state = json.load(self.state_file_path.open())
            self.active = True
            self.current_system =               state["current_system"]
            self.system_coordinates =           tuple(state["system_coordinates"])
            self.system_address =               state["system_address"]
            self.bodies =                       state["bodies"]
            self.stars =                        state["stars"]
            self.clusters =                     state["clusters"]
            self.icy_bodies =                   state["icy_bodies"]
            self.rocky_icy_bodies =             state["rocky_icy_bodies"]
            self.rocky_bodies =                 state["rocky_bodies"]
            self.metal_rich_bodies =            state["metal_rich_bodies"]
            self.high_metal_content_bodies =    state["HMC_bodies"]
            self.earth_like_world_bodies =      state["ELW_bodies"]
            self.ammonia_world_bodies =         state["AW_bodies"]
            self.water_world_bodies =           state["WW_bodies"]
            self.gas_giant_bodies =             state["Gas_giant_bodies"]
            self.landables =                    state["landables"]
            self.atmospherics =                 state["atmospherics"]
            self.ringed =                       state["ringed"]
            self.terraformables =               state["terraformables"]
            self.volcanisms =                   state["volcanisms"]
            self.biologicals =                  state["biologicals"]
            self.geologicals =                  state["geologicals"]
            self.guardians =                    state["guardians"]
            self.thargoids =                    state["thargoids"]

    def process_past_event(self, event: Any) -> None:
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
            case "Scan":
                self.bodies[event["BodyID"]][event["event"]] = event
                if "Rings" in event:
                    self.ringed.add(event["BodyID"])
                if "StarType" in event:
                    self.stars.add(event["BodyID"])
                else:
                    if "TerraformState" in event:
                        if event["TerraformState"] == "Terraformable":
                            self.terraformables.add(event["BodyID"])
                    if "AtmosphereType" in event:
                        if event["AtmosphereType"] != "None":
                            self.atmospherics.add(event["BodyID"])
                    if "Volcanism" in event:
                        if event["Volcanism"]:
                            self.volcanisms.add(event["BodyID"])
                    if "Landable" in event:
                        if event["Landable"]:
                            self.landables.add(event["BodyID"])
                    if "PlanetClass" in event:
                        match event["PlanetClass"]:
                            case "Icy body":                self.icy_bodies.add(event["BodyID"])
                            case "Rocky ice body":          self.rocky_icy_bodies.add(event["BodyID"])
                            case "Rocky body":              self.rocky_bodies.add(event["BodyID"])
                            case "Metal rich body":         self.metal_rich_bodies.add(event["BodyID"])
                            case "High metal content body": self.high_metal_content_bodies.add(event["BodyID"])
                            case "Earth-like world":        self.earth_like_world_bodies.add(event["BodyID"])
                            case "Ammonia world":           self.ammonia_world_bodies.add(event["BodyID"])
                            case "Water world":             self.water_world_bodies.add(event["BodyID"])
                            case _:                         self.gas_giant_bodies.add(event["BodyID"])
                    else:
                        self.clusters.add(event["BodyID"])
                self.save_state()
            case "FSSBodySignals":
                self.bodies[event["BodyID"]][event["event"]] = event
                bodyID = int(event["BodyID"])
                for signal in event["Signals"]:
                    match signal["Type"]:
                        case "$SAA_SignalType_Biological;":
                            self.biologicals.add(bodyID)
                        case "$SAA_SignalType_Geological;":
                            self.geologicals.add(bodyID)
                        case "$SAA_SignalType_Guardian;":
                            self.guardians.add(bodyID)
                        case "$SAA_SignalType_Thargoid;":
                            self.thargoids.add(bodyID)
                        case _: pass
                    self.save_state()
            case "SAAScanComplete":
                self.bodies[event["BodyID"]][event["event"]] = event
                self.save_state()
            case "SAASignalsFound":
                self.bodies[event["BodyID"]][event["event"]] = event
                self.save_state()
            case "StartJump":
                self.bodies.clear()
                self.stars.clear()
                self.clusters.clear()
                self.icy_bodies.clear()
                self.rocky_icy_bodies.clear()
                self.rocky_bodies.clear()
                self.metal_rich_bodies.clear()
                self.high_metal_content_bodies.clear()
                self.earth_like_world_bodies.clear()
                self.ammonia_world_bodies.clear()
                self.water_world_bodies.clear()
                self.gas_giant_bodies.clear()
                self.landables.clear()
                self.atmospherics.clear()
                self.ringed.clear()
                self.volcanisms.clear()
                self.terraformables.clear()
                self.biologicals.clear()
                self.geologicals.clear()

                self.save_state()
            case "FSDJump":
                previous_coordinates = self.system_coordinates
                self.current_system = event["StarSystem"]
                self.system_coordinates = (event["StarPos"][0], event["StarPos"][1], event["StarPos"][2])
                self.system_address = event["SystemAddress"]
                self.save_state()
                distance_jumped = get_distance(previous_coordinates, self.system_coordinates)
                print("Jumped " + str(round(distance_jumped, 2)) + "Ly to system: " + self.current_system)
            case _: pass

class FSSReporter(Program):
    SURVEY_NAME = "fss_reporter"
    core_program: CoreProgram

    def __init__(self, core_program: CoreProgram) -> None:
        super().__init__()
        self.core_program = core_program

    def process_event(self, event: Any) -> None:
        match event["event"]:
            case "FSSAllBodiesFound":
                print(bright_cyan("\nFull system scan of " + self.core_program.current_system + " complete!\n"))
                valuables: list[str] = []
                for valuable in self.core_program.terraformables | self.core_program.earth_like_world_bodies | self.core_program.ammonia_world_bodies | self.core_program.water_world_bodies:
                    attributes = str(
                                " (" + 
                                        str(self.core_program.bodies[valuable]["Scan"]["PlanetClass"]) + 
                                        str(" + Terraformable" if valuable in self.core_program.terraformables else "") + 
                                        ")"
                                    )
                    valuables.append(self.core_program.bodies[valuable]["Scan"]["BodyName"] + attributes)
                if valuables:
                    print(bright_blue("Valuable planets: " + str(len(valuables))))
                    for valuable in valuables:
                        print(bright_blue("\t" + str(valuable)))
                if self.core_program.biologicals:
                    print(bright_green("Biological signatures: " + str(len(self.core_program.biologicals)) + " (" + str(len(self.core_program.biologicals)) + ")"))
                    for biological in self.core_program.biologicals:
                        print(bright_green("\t" + str(self.core_program.bodies[biological]["FSSBodySignals"]["BodyName"])))
                if self.core_program.geologicals:
                    print(yellow("Geological signatures: " + str(len(self.core_program.geologicals)) + " (" + str(len(self.core_program.geologicals)) + ")"))
                    for geological in self.core_program.geologicals:
                        print(yellow("\t" + str(self.core_program.bodies[geological]["FSSBodySignals"]["BodyName"])))
            case _: pass

class BoxelSurvey(Program):
    SURVEY_NAME = "boxel_survey"
    boxel_log_file_path: Path
    system_list_file_path: Path
    system_list: list[str]
    next_system: str
    core_program: Program

    def __init__(self, core_program: Program) -> None:
        super().__init__()
        self.boxel_log_file_path = self.survey_dir / Path("boxel_log")
        self.system_list_file_path = self.survey_dir / Path("boxel_survey_system_list")
        self.core_program = core_program

    def save_state(self) -> None:
        state: dict[str, Any] = {"active":self.active}
        json.dump(state, self.state_file_path.open("w"))

    def load_state(self) -> None:
        if self.state_file_path.exists():
            state = json.load(self.state_file_path.open())
            self.active = state["active"]

    def process_past_event(self, event: Any) -> None:
        pass
    
    def process_event(self, event: Any) -> None:
        match event["event"]:
            case "FSDJump":
                if self.next_system.lower() == event["StarSystem"].lower():
                    reserialize_file(self.system_list_file_path, self.system_list)
                    open(self.boxel_log_file_path, "a").write(self.next_system + "\n")
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
    SURVEY_NAME = "density_column_survey"

    def __init__(self) -> None:
        if not self.survey_dir.exists():
            self.survey_dir.mkdir()
        self.load_state()
        self.save_state()

    def process_event(self, event: Any) -> None:
        match event["event"]:
            case "FSDJump":
                coordinates_and_system = f'{event["StarPos"][0]}\t{event["StarPos"][1]}\t{event["StarPos"][2]}\t{event["StarSystem"]}'
                text_to_clipboard(coordinates_and_system)
            case _: pass

class DensityNavRouteSurvey(Program):
    pass

