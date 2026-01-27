from collections import defaultdict
from typing import Any
from pathlib import Path
from src.util import text_to_clipboard, get_distance, reserialize_file, read_file_by_lines
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
import math
import json

global_style = Style.from_dict({
    "error": "#ff0000",
})

class Program():
    style = Style.from_dict({
        "survey_color": "#ffffff",
    })

    SURVEY_NAME: str = "UNNAMED_SURVEY"
    survey_dir: Path
    state_file_path: Path
    enabled: bool = False

    def __init__(self) -> None:
        self.print("Loading module...", end="")
        self.survey_dir = Path("surveys") / Path(self.SURVEY_NAME.lower())
        self.state_file_path = self.survey_dir / Path(self.SURVEY_NAME.lower() + "_state")
        if not self.survey_dir.exists():
            self.survey_dir.mkdir()
        try:
            self.load_state()
            self.print("Enabled" if self.enabled else "Disabled", prefix="")
            self.save_state()
        except Exception as e: # pyright: ignore[reportUnusedVariable]
            print("")
            self.print("Initializing a new state file... First time running? Or previous state file corrupted!")
            self.enabled = False
            self.print("Disabled")
            self.save_state()
        self.style = Style(self.style.style_rules + global_style.style_rules)

    def enable(self) -> None:
        self.enabled = True
        self.save_state()
        self.print("enabled!")

    def disable(self) -> None:
        self.enabled = False
        self.save_state()
        self.print("disabled!")

    def save_state(self) -> None:
        state: dict[str, Any] = {"active":self.enabled}
        json.dump(state, self.state_file_path.open("w"))

    def load_state(self) -> None:
        if self.state_file_path.exists():
            state = json.load(self.state_file_path.open())
            self.enabled = state["active"]

    def process_past_event(self, event: Any) -> None:
        pass

    def process_event(self, event: Any) -> None:
        pass

    def process_user_input(self, arguments: list[str]) -> None:
        if len(arguments) == 0:
            return
        elif arguments[0] == self.SURVEY_NAME.lower():
            if len(arguments) < 2:
                self.print("<error>Received no commands!</error>")
                return
            match arguments[1]:
                case "enable":
                    self.enable()
                case "disable":
                    self.disable()
                case _: self.print("<error>Received unknown command - </error>" + arguments[1])

    def print(self, *values: object, sep: str | None = " ", end: str | None = "\n", prefix: str | None = None) -> None:
        if prefix is not None:
            print_formatted_text(prefix, *values, sep=sep, end=end, style=self.style) # pyright: ignore[reportArgumentType]
        else:
            print_formatted_text(HTML(f"<survey_color>{self.SURVEY_NAME}</survey_color>: "), *values, sep=sep, end=end, style=self.style) # pyright: ignore[reportArgumentType]


class CoreProgram(Program):
    style = Style.from_dict({
        "survey_color": "#ff7700",
    })
    SURVEY_NAME = "core"
    active = True
    commander_greeted = False
    current_system: str = ""
    system_coordinates: tuple[float, float, float] = (0.0, 0.0, 0.0)
    system_address: int = 0
    bodies: defaultdict[int, dict[str, Any]] = defaultdict(dict)
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
        self.enabled = True
        self.save_state()
        self.print("ESST: Core module is always enabled!")

    def disable(self) -> None:
        self.enabled = True
        self.save_state()
        self.print("ESST: Core module cannot be disabled!")

    def save_state(self) -> None:
        state: dict[str, Any] = {
                "active":                       self.enabled,
                "current_system":               self.current_system,
                "system_coordinates":           self.system_coordinates,
                "system_address":               self.system_address,
                "bodies":                       self.bodies,
                "stars":                        list(self.stars),
                "clusters":                     list(self.clusters),
                "icy_bodies":                   list(self.icy_bodies),
                "rocky_icy_bodies":             list(self.rocky_icy_bodies),
                "rocky_bodies":                 list(self.rocky_bodies),
                "metal_rich_bodies":            list(self.metal_rich_bodies),
                "high_metal_content_bodies":    list(self.high_metal_content_bodies),
                "earth_like_world_bodies":      list(self.earth_like_world_bodies),
                "ammonia_world_bodies":         list(self.ammonia_world_bodies),
                "water_world_bodies":           list(self.water_world_bodies),
                "gas_giant_bodies":             list(self.gas_giant_bodies),
                "landables":                    list(self.landables),
                "atmospherics":                 list(self.atmospherics),
                "ringed":                       list(self.ringed),
                "volcanisms":                   list(self.volcanisms),
                "terraformables":               list(self.terraformables),
                "biologicals":                  list(self.biologicals),
                "geologicals":                  list(self.geologicals),
                "guardians":                    list(self.guardians),
                "thargoids":                    list(self.thargoids),
            }
        json.dump(state, self.state_file_path.open("w"))

    def load_state(self) -> None:
        if self.state_file_path.exists():
            state = json.load(self.state_file_path.open())
            self.enabled = True
            self.current_system =               state["current_system"]
            self.system_coordinates =           tuple(state["system_coordinates"])
            self.system_address =               state["system_address"]
            self.bodies =                       defaultdict(dict, state["bodies"])
            self.stars =                        set(state["stars"])
            self.clusters =                     set(state["clusters"])
            self.icy_bodies =                   set(state["icy_bodies"])
            self.rocky_icy_bodies =             set(state["rocky_icy_bodies"])
            self.rocky_bodies =                 set(state["rocky_bodies"])
            self.metal_rich_bodies =            set(state["metal_rich_bodies"])
            self.high_metal_content_bodies =    set(state["high_metal_content_bodies"])
            self.earth_like_world_bodies =      set(state["earth_like_world_bodies"])
            self.ammonia_world_bodies =         set(state["ammonia_world_bodies"])
            self.water_world_bodies =           set(state["water_world_bodies"])
            self.gas_giant_bodies =             set(state["gas_giant_bodies"])
            self.landables =                    set(state["landables"])
            self.atmospherics =                 set(state["atmospherics"])
            self.ringed =                       set(state["ringed"])
            self.terraformables =               set(state["terraformables"])
            self.volcanisms =                   set(state["volcanisms"])
            self.biologicals =                  set(state["biologicals"])
            self.geologicals =                  set(state["geologicals"])
            self.guardians =                    set(state["guardians"])
            self.thargoids =                    set(state["thargoids"])

    def process_past_event(self, event: Any) -> None:
        match event["event"]:
            case "Commander":
                if not self.commander_greeted:
                    self.print("Welcome, Commander " + event["Name"])
                    self.commander_greeted = True
            case _: pass

    def process_event(self, event: Any) -> None:
        self.print(event["event"])
        match event["event"]:
            case "Shutdown":
                exit("Elite Stellar Survey Tools spooling down...\nFarewell, Commander!")
            case "Scan":
                self.bodies[int(event["BodyID"])][event["event"]] = event
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
                self.bodies[int(event["BodyID"])][event["event"]] = event
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
                self.print("Jumped " + str(round(distance_jumped, 2)) + "Ly to system: " + self.current_system)
            case _: pass

class FSSReporter(Program):
    style = Style.from_dict({
        "survey_color": "#00ffff",
        "terraformables": "#6060ff",
        "biologicals": "#00ff00",
        "geologicals": "#ffff00",
    })

    SURVEY_NAME = "FSSReporter"
    core: CoreProgram

    def __init__(self, core: CoreProgram) -> None:
        super().__init__()
        self.core = core

    def process_event(self, event: Any) -> None:
        match event["event"]:
            case "FSSAllBodiesFound":
                self.print(HTML("<survey_color>\nFull system scan of " + self.core.current_system + " complete!</survey_color>\n"))
                valuables: list[str] = []
                for valuable in self.core.terraformables | self.core.earth_like_world_bodies | self.core.ammonia_world_bodies | self.core.water_world_bodies:
                    attributes = str(
                                " (" + 
                                        str(self.core.bodies[valuable]["Scan"]["PlanetClass"]) + 
                                        str(" + Terraformable" if valuable in self.core.terraformables else "") + 
                                        ")"
                                    )
                    valuables.append(self.core.bodies[valuable]["Scan"]["BodyName"] + attributes)
                if valuables:
                    self.print(HTML("<terraformables>Valuable planets: " + 
                                    str(len(valuables)) + 
                                    "</terraformables>"), 
                                    prefix="")
                    for valuable in valuables:
                        self.print(HTML("<terraformables>\t" + 
                                   str(valuable) + 
                                   "</terraformables>"), 
                                   prefix="")
                if self.core.biologicals:
                    self.print(HTML("<biologicals>Biological signatures: " + 
                                    str(len(self.core.biologicals)) + 
                                    " (" + 
                                    str(len(self.core.biologicals)) + 
                                    ")</biologicals>"), 
                                    prefix="")
                    for biological in self.core.biologicals:
                        self.print(HTML("<biologicals>\t" + 
                                   str(self.core.bodies[biological]["FSSBodySignals"]["BodyName"]) + 
                                   "</biologicals>"), 
                                   prefix="")
                if self.core.geologicals:
                    self.print(HTML("<geologicals>Geological signatures: " + 
                                    str(len(self.core.geologicals)) + 
                                    " (" + 
                                    str(len(self.core.geologicals)) + 
                                    ")</geologicals>"), 
                                    prefix="")
                    for geological in self.core.geologicals:
                        self.print(HTML("<geologicals>\t" + 
                                        str(self.core.bodies[geological]["FSSBodySignals"]["BodyName"]) + 
                                        "</geologicals>"), 
                                        prefix="")
            case _: pass

class BoxelSurvey(Program):
    style = Style.from_dict({
        "survey_color": "#ffff00",
    })

    SURVEY_NAME = "BoxelSurvey"
    boxel_log_file_path: Path
    system_list_file_path: Path
    system_list: list[str]
    next_system: str
    core: Program

    def __init__(self, core: Program) -> None:
        super().__init__()
        self.boxel_log_file_path = self.survey_dir / Path("boxel_log")
        self.system_list_file_path = self.survey_dir / Path("boxel_survey_system_list")
        self.core = core

    def process_past_event(self, event: Any) -> None:
        pass
    
    def process_event(self, event: Any) -> None:
        match event["event"]:
            case "FSDJump":
                if self.next_system.lower() == event["StarSystem"].lower():
                    reserialize_file(self.system_list_file_path, self.system_list)
                    open(self.boxel_log_file_path, "a").write(self.next_system + "\n")
                    if not self.system_list:
                        self.print(HTML(" <survey_color>Survey Completed!</survey_color> "))
                        self.disable()
                        self.save_state()
                        return
                    self.next_system = self.load_next_system()
                    text_to_clipboard(self.next_system)
                    self.print(HTML("Next system: " + self.next_system))
            case _: pass

    def load_next_system(self) -> str:
        return self.system_list.pop(0)

class DW3DensityColumnSurvey(Program):
    style = Style.from_dict({
        "survey_color": "#ff00ff",
    })

    SURVEY_NAME = "DW3DensityColumnSurvey"
    MAX_HEIGHT_DEVIATION = 10
    survey_file_path: Path = Path("")
    core: CoreProgram
    system_in_sequence: int = 0
    start_height = 0
    direction: int = 0
    valid_system = False
    system_surveyed = False
    survey_ongoing = False

    def __init__(self, core: CoreProgram) -> None:
        super().__init__()
        self.survey_file_path = Path(self.survey_dir / "default.tsv")
        self.save_state()
        self.core = core

    def save_state(self) -> None:
        state: dict[str, Any] = {}
        state["active"] = self.enabled
        state["system_in_sequence"] = self.system_in_sequence
        state["survey_file_path"] = str(self.survey_file_path)
        state["start_height"] = self.start_height
        state["direction"] = self.direction
        state["valid_system"] = self.valid_system
        state["system_surveyed"] = self.system_surveyed
        state["survey_ongoing"] = self.survey_ongoing
        json.dump(state, self.state_file_path.open("w"))

    def load_state(self) -> None:
        if self.state_file_path.exists():
            state = json.load(self.state_file_path.open())
            self.enabled = state["active"]
            self.survey_file_path = Path(str(state["survey_file_path"]))
            self.system_in_sequence = state["system_in_sequence"]
            self.start_height = state["start_height"]
            self.direction = state["direction"]
            self.valid_system = state["valid_system"]
            self.system_surveyed = state["system_surveyed"]
            self.survey_ongoing = state["survey_ongoing"]

    def process_event(self, event: Any) -> None:
        if self.survey_ongoing:
            match event["event"]:
                case "FSDJump":
                    current_height = self.core.system_coordinates[1]
                    if abs(current_height - self.get_expected_galactic_height()) < self.MAX_HEIGHT_DEVIATION:
                        self.valid_system = True
                        self.print("System valid for survey!")
                case _: pass
        else: pass

    def is_valid_starting_height(self, galactic_height: float, direction: str) -> bool:
        return True if (abs(galactic_height - 1000) < self.MAX_HEIGHT_DEVIATION and direction == "down") or \
                (abs(galactic_height + 1000) < self.MAX_HEIGHT_DEVIATION and direction == "up") or \
                (abs(galactic_height) < self.MAX_HEIGHT_DEVIATION ) else False
    
    def get_expected_galactic_height(self) -> float:
        return self.start_height + 50 * self.direction * self.system_in_sequence
    
    def process_user_input(self, arguments: list[str]) -> None:

        # TODO: Refactor this mess

        if len(arguments) > 1:
            if arguments[0] in ["dcs", "dc", "column", "densitycolumn", "densitycolumnsurvey", "dw3densitycolumnsurvey"] and self.enabled:
                galactic_height = self.core.system_coordinates[1]
                count = 0
                distance = 0.0
                match arguments[1]:
                    case "start" | "begin":
                        if len(arguments) < 3:
                            self.print("<error>Direction parameter required to start survey!</error>")
                            return
                        if arguments[2] not in ["up", "ascending", "down", "descending"]:
                            self.print("<error>Invalid direction parameter - Must be 'up', 'ascending', 'down', or 'descending'!</error>")
                            return
                        if self.is_valid_starting_height(galactic_height, arguments[2]):
                            self.direction = 1 if arguments[2] in ["up", "ascending"] else -1
                            self.valid_system = True
                            self.start_height = -1000 if galactic_height < -500 else 0 if galactic_height < 500 else 1000
                            self.system_in_sequence = 0
                            self.survey_ongoing = True
                            self.survey_file_path = Path(self.survey_dir / str(self.core.current_system + ".tsv"))
                            self.enable()
                            self.save_state()
                            self.print("<survey_color>Started Density Column Survey from system: </survey_color>" + self.core.current_system)
                            self.print("Please make sure to enter current system's count and max distance before continuing!")
                            return
                        else:
                            self.print("<error>Will not start the survey - Too far from a valid startpoint!</error>")
                            self.print("Please move to a galactic height of -1000, 0, or 1000 +-" + str(self.MAX_HEIGHT_DEVIATION) + "Ly and try again!")
                            return
                        
                    case "undo":
                        survey = read_file_by_lines(self.survey_file_path)
                        if len(survey) > 0:
                            removed = survey.pop(0).split()
                            self.print("Removed datapoint: " + removed[0])
                        else:
                            self.print("No datapoints to remove!")
                            return
                        reserialize_file(self.survey_file_path, survey)
                        self.system_in_sequence -= 1
                        self.system_surveyed = False
                        self.process_event({"event":"FSDJump"})
                        self.save_state()

                    case "reset" | "clear":
                        self.survey_file_path.unlink(missing_ok=True)
                        self.system_in_sequence = 0
                        self.survey_file_path = Path(self.survey_dir / "default.tsv")
                        self.valid_system = False
                        self.system_surveyed = False
                        self.start_height = 0
                        self.direction = 0
                        self.survey_ongoing = False
                        self.print("Cleared current survey progress.")
                        self.save_state()
                        return
                    
                    case "enable" | "disable":
                        super().process_user_input(arguments)

                    case _:
                        if self.survey_ongoing:
                            try:
                                count = abs(int(arguments[1]))
                                if count > 49:
                                    self.print("<error>Count value cannot exceed 49!</error>\n" +
                                    "Make sure you counted the number of neighboring systems in the nav panel correctly" +
                                    "and make sure no FSD route is planned.")
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
            else:
                super().process_user_input(arguments)
                
    def process_datapoint(self, count: int, distance: float) -> None:
        current_height = self.core.system_coordinates[1]
        if not self.valid_system:
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
        datapoint = str(
            str(self.core.current_system) + "\t" +
            str(self.get_expected_galactic_height()) + "\t" +
            str(count) + "\t" +
            str(count + 1) + "\t" +
            str(distance) + "\t" +
            str(rho) + "\t" +
            str(self.core.system_coordinates[0]) + "\t" +
            str(self.core.system_coordinates[2]) + "\t" +
            str(self.core.system_coordinates[1])
        )
        open(self.survey_file_path, "a").write(json.dumps(datapoint) + "\n")
        self.print("<survey_color>Recorded datapoint for system: </survey_color>" + self.core.current_system)
        self.print(datapoint)
        self.system_in_sequence += 1
        self.system_surveyed = True
        self.valid_system = False
        self.save_state()
        if self.system_in_sequence == 20:
            self.print("<survey_color>Survey completed!</survey_color>\n")
            self.system_in_sequence = 0
            self.system_surveyed = False
            self.save_state()
            return
        


class DensityNavRouteSurvey(Program):
    pass

