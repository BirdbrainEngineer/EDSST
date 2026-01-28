from enum import Enum, auto
from typing import Any
from pathlib import Path
from src.util import text_to_clipboard, get_distance, reserialize_file, read_file_by_lines, abbreviate_planet_type
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from src.version import MODULE_VERSIONS_PATH
import msgspec
import math
import json
import asyncio

# TODO: rename "program into module"
# TODO: separate each module into their own file

global_style = Style.from_dict({
    "error": "#ff4040",
    "warning": "#ffff80",
    "red": "#ff0000",
    "orange": "#FF8000",
    "yellow": "#ffff00",
    "lime": "#80ff00",
    "green": "#00ff00",
    "mint": "#00ff80",
    "cyan": "#00ffff",
    "bright-blue": "#0080ff",
    "blue": "#0000ff",
    "violet": "#8000ff",
    "magenta": "#ff00ff",
    "deep-pink": "#ff0080",
    "white": "#ffffff",
    "black": "#000000",
    "dark-grey": "#404040",
    "grey": "#808080",
    "light-grey": "#b0b0b0",
})

class ModuleState(msgspec.Struct):
    enabled: bool = False

class Program():
    style = Style.from_dict({
        "survey_color": "#ffffff",
    })

    SURVEY_NAME: str = "UNNAMED_SURVEY"
    SURVEY_VERSION: str = "?"
    survey_dir: Path
    state_file_path: Path
    caught_up: bool = True
    state: ModuleState = ModuleState()

    def __init__(self) -> None:
        first_boot = False
        version_changed = False
        previous_version: str = "N/A"
        self.style = Style(self.style.style_rules + global_style.style_rules)
        self.print("Loading module version " + self.SURVEY_VERSION + "...")
        self.survey_dir = Path("surveys") / Path(self.SURVEY_NAME.lower())
        self.state_file_path = self.survey_dir / Path(self.SURVEY_NAME.lower() + "_state")
        if not self.survey_dir.exists():
            self.survey_dir.mkdir()
            first_boot = True
        
        try:
            module_versions = json.load(MODULE_VERSIONS_PATH.open())
            first_boot = True
            for module in module_versions:
                if module["module_name"] == self.SURVEY_NAME:
                    first_boot = False
                    if module["version"] != self.SURVEY_VERSION:
                        module["version"] = self.SURVEY_VERSION
                        version_changed = True
                        json.dump(module_versions, MODULE_VERSIONS_PATH.open("w"))
                        break
            module_versions.append({"module_name": self.SURVEY_NAME, "version": self.SURVEY_VERSION})
            try:
                json.dump(module_versions, MODULE_VERSIONS_PATH.open("w"))
            except:
                self.print("<error>Could not add to versions file! EDSST is in a peculiar state... Tread with caution.</error>")
        except Exception as e: # pyright: ignore[reportUnusedVariable]
            if MODULE_VERSIONS_PATH.exists():
                self.print("Could not load version file!")
            else:
                self.print("<error>Could not find versions file!</error>")
                self.print("<warning>Attempting to make one.</warning>")
                module_versions: list[dict[str, Any]] = [{"module_name": self.SURVEY_NAME, "version": self.SURVEY_VERSION}]
                first_boot = True
                try:
                    json.dump(module_versions, MODULE_VERSIONS_PATH.open("w"))
                    self.print("<yellow>New versions file successfully created.</yellow>")
                except:
                    self.print("<error>Could not make a versions file! EDSST is in a peculiar state... Tread with caution.</error>")

        if first_boot: self.print("<warning>First boot of module detected!</warning>")
        if version_changed: 
            self.print("<warning>New module version detected!</warning> ")
            self.print(previous_version + " -> " + self.SURVEY_VERSION)

        try:
            self.load_state()
            self.save_state()
        except Exception as ex: # pyright: ignore[reportUnusedVariable]
            raise ex
            if not first_boot or not version_changed:
                self.print("<error>State file was found to be corrupted or missing! Data loss or corruption is possible!</error>")
            self.print("<warning>Initializing a new state file...</warning>")
            self.save_state()
        self.print("Module successfully loaded!")
        if self.state.enabled:
            self.print("Module currently <green>enabled</green>")
        else:
            self.print("Module currently <red>disabled</red>")

    def enable(self) -> None:
        if self.state.enabled:
            self.print("<green>Already enabled!</green>")
        else:
            self.state.enabled = True
            self.save_state()
            self.print("<green>Enabled!</green>")

    def disable(self) -> None:
        if not self.state.enabled:
            self.print("<red>Already disabled!</red>")
        else:
            self.state.enabled = False
            self.save_state()
            self.print("<red>Disabled!</red>")

    def save_state(self) -> None:
        state: dict[str, Any] = {"enabled":self.state.enabled}
        self.state_file_path.write_bytes(msgspec.json.encode(state))

    def load_state(self) -> None:
        if self.state_file_path.exists():
            self.state = msgspec.json.decode(self.state_file_path.read_bytes(), type = ModuleState)

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:
        if event["event"] == "CaughtUp":
            self.caught_up = True

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        if len(arguments) == 0:
            return
        elif arguments[0].lower() == self.SURVEY_NAME.lower():
            if len(arguments) < 2:
                self.print("<warning>Received no commands!</warning>")
                return
            match arguments[1]:
                case "enable":
                    self.enable()
                case "disable":
                    self.disable()
                case _: self.print("<warning>Received unknown command - </warning>" + arguments[1])

    def print(self, *values: str, sep: str = " ", end: str = "\n", prefix: str | None = None) -> None:
        if not self.caught_up: return
        html = sep.join(values)
        prefix = prefix if prefix != None else f"<survey_color>{self.SURVEY_NAME}</survey_color>:"
        if prefix:
            html = prefix + html
        print_formatted_text(HTML(html), sep=sep, end=end, style=self.style)

class BodyAttribute(Enum):
    first_discovery = auto()
    first_discovery_cluster = auto()
    first_discovery_star = auto()
    first_discovery_planet = auto()
    first_possible_map = auto()
    first_possible_map_planet = auto()
    first_possible_footfall = auto()
    first_possible_footfall_planet = auto()
    first_map = auto()
    first_footfall = auto()
    automatic_scan = auto()
    fss_scan = auto()
    fss_signal = auto()
    saa_scan = auto()
    saa_signal = auto()
    cluster = auto()
    star = auto()
    planet = auto()
    icy_body = auto()
    rocky_icy_body = auto()
    rocky_body = auto()
    metal_rich_body = auto()
    high_metal_content_body = auto()
    earth_like_world_body = auto()
    ammonia_world_body = auto()
    water_world_body = auto()
    gas_giant_body = auto()
    landable = auto()
    atmospheric = auto()
    ringed = auto()
    terraformable = auto()
    volcanic = auto()
    bios = auto()
    geos = auto()
    guardians = auto()
    thargoids = auto()

class Bodies(msgspec.Struct):
    bodies: dict[int, dict[str, Any]] = msgspec.field(default_factory=dict) # pyright: ignore[reportUnknownVariableType]
    bodies_by_attribute: dict[BodyAttribute, set[int]] = msgspec.field(default_factory=lambda: {attribute: set() for attribute in BodyAttribute})

    def get_bodies_by_attribute(self, *args: BodyAttribute, sorted: bool = False):
        query_set: set[int] = set()
        for attribute in args:
            query_set = query_set | self.bodies_by_attribute[attribute]

        query_list = list(query_set)
        if sorted: query_list.sort()
        result: list[dict[str, Any]] = []
        for bodyID in query_list:
            result.append(self.bodies[bodyID])
        return result

    def get_body_by_id(self, body_id: int) -> dict[str, Any]:
        if body_id not in self.bodies:
            self.bodies[body_id] = {}
        return self.bodies[body_id]
    
    def get_bodies_by_id(self, body_ids: list[int]):
        result: list[dict[str, Any]] = []
        for id in body_ids:
            result.append(self.get_body_by_id(id))
        return result
    
    def add_body_signal(self, body_event: dict[str, Any]) -> None:
        self.get_body_by_id(body_event["BodyID"]).update(body_event)

    def record_attribute(self, attribute: BodyAttribute, bodyID: int) -> None:
        self.bodies_by_attribute[attribute].add(bodyID)
class StarSystem(msgspec.Struct):
    name: str = ""
    coordinates: tuple[float, float, float] = (0.0, 0.0, 0.0)
    address: int = 0
    num_bodies: int = 0
    num_non_bodies: int = 0
    bodies: Bodies = msgspec.field(default_factory=lambda: Bodies())

class CoreProgramState(ModuleState):
    enabled: bool = True
    event_stream_enabled: bool = False
    current_system: StarSystem = msgspec.field(default_factory=StarSystem)
    previous_system: StarSystem = msgspec.field(default_factory=StarSystem)

class CoreProgram(Program):
    style = Style.from_dict({
        "survey_color": "#ff8000",
    })

    SURVEY_NAME = "core"
    SURVEY_VERSION: str = "0.0.1"
    commander_greeted = False
    commander_name: str = ""
    state: CoreProgramState = CoreProgramState()

    # TODO: separate out different gas giant types

    def __init__(self) -> None:
        super().__init__()

    def disable(self) -> None:
        super().disable()
        self.print("<error>Disabling the core module can have unforseen side-effects!</error>")
        self.print("<error>Consider re-enabling, unless you really know what you are doing!</error>")

    def save_state(self) -> None:
        if not self.caught_up: return
        self.state_file_path.write_bytes(msgspec.json.encode(self.state))

    def load_state(self) -> None:
        if self.state_file_path.exists():
            self.state = msgspec.json.decode(self.state_file_path.read_bytes(), type = CoreProgramState) # pyright: ignore[reportIncompatibleVariableOverride]

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        if arguments[0] in ["core", "main", "base", "edsst"]:
            match arguments[1]:
                case "eventstream":
                    if len(arguments) < 3: pass
                    match arguments[2]:
                        case "enable" | "on":
                            if self.state.event_stream_enabled: 
                                self.print("<yellow>Display of Event Stream already enabled!</yellow>")
                            else:
                                self.state.event_stream_enabled = True
                                self.save_state()
                                self.print("Event Stream is now displayed.")
                        case "disable" | "off":
                            if not self.state.event_stream_enabled: 
                                self.print("<yellow>Display of Event Stream already disabled!</yellow>")
                            else:
                                self.state.event_stream_enabled = False
                                self.save_state()
                                self.print("Event Stream is no longer displayed.")
                        case _: pass
                case _: await super().process_user_input(arguments, tg)

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:
        await super().process_event(event, tg)
        if self.state.event_stream_enabled: self.print(event["event"])
        bodyID = -1
        if "BodyID" in event: bodyID = int(event["BodyID"])
        match event["event"]:
            case "Commander":
                name = str(event["Name"])
                if not self.commander_greeted or name != self.commander_name:
                    self.print("Welcome, Commander " + name)
                    self.commander_name = str(name)
                    self.commander_greeted = True
            case "Scan":
                is_star = True if "StarType" in event else False
                is_cluster = True if "Cluster" in str(event["BodyName"]) else False
                self.state.current_system.bodies.add_body_signal(event)
                if event["WasDiscovered"] == False:         
                    self.state.current_system.bodies.record_attribute(BodyAttribute.first_discovery, bodyID)
                    if is_cluster:                          self.state.current_system.bodies.record_attribute(BodyAttribute.first_discovery_cluster, bodyID)
                    else:
                        if is_star:                         self.state.current_system.bodies.record_attribute(BodyAttribute.first_discovery_star, bodyID)
                        else:                               self.state.current_system.bodies.record_attribute(BodyAttribute.first_discovery_planet, bodyID)
                if event["WasMapped"] == False:             
                    self.state.current_system.bodies.record_attribute(BodyAttribute.first_possible_map, bodyID)
                    if not is_cluster and not is_star:
                        self.state.current_system.bodies.record_attribute(BodyAttribute.first_possible_map_planet, bodyID)
                if event["WasFootfalled"] == False:         
                    self.state.current_system.bodies.record_attribute(BodyAttribute.first_possible_footfall, bodyID)
                    if not is_cluster and not is_star:
                        self.state.current_system.bodies.record_attribute(BodyAttribute.first_possible_footfall_planet, bodyID)
                if is_cluster:                              self.state.current_system.bodies.record_attribute(BodyAttribute.cluster, bodyID)
                else:
                    if "Rings" in event:                    self.state.current_system.bodies.record_attribute(BodyAttribute.ringed, bodyID)
                    if is_star:                             self.state.current_system.bodies.record_attribute(BodyAttribute.star, bodyID)
                    else:
                        if event["TerraformState"]:         self.state.current_system.bodies.record_attribute(BodyAttribute.terraformable, bodyID)
                        if event["Volcanism"]:              self.state.current_system.bodies.record_attribute(BodyAttribute.volcanic, bodyID)
                        if event["Landable"]:               self.state.current_system.bodies.record_attribute(BodyAttribute.landable, bodyID)
                        if "AtmosphereType" in event:
                            if event["AtmosphereType"] != "None": 
                                                            self.state.current_system.bodies.record_attribute(BodyAttribute.atmospheric, bodyID)
                        match event["PlanetClass"]:
                            case "Icy body":                self.state.current_system.bodies.record_attribute(BodyAttribute.icy_body, bodyID)
                            case "Rocky ice body":          self.state.current_system.bodies.record_attribute(BodyAttribute.rocky_icy_body, bodyID)
                            case "Rocky body":              self.state.current_system.bodies.record_attribute(BodyAttribute.rocky_body, bodyID)
                            case "Metal rich body":         self.state.current_system.bodies.record_attribute(BodyAttribute.metal_rich_body, bodyID)
                            case "High metal content body": self.state.current_system.bodies.record_attribute(BodyAttribute.high_metal_content_body, bodyID)
                            case "Earthlike body":        self.state.current_system.bodies.record_attribute(BodyAttribute.earth_like_world_body, bodyID)
                            case "Ammonia world":           self.state.current_system.bodies.record_attribute(BodyAttribute.ammonia_world_body, bodyID)
                            case "Water world":             self.state.current_system.bodies.record_attribute(BodyAttribute.water_world_body, bodyID)
                            case _:                         self.state.current_system.bodies.record_attribute(BodyAttribute.gas_giant_body, bodyID)
                        self.state.current_system.bodies.record_attribute(BodyAttribute.planet, bodyID)
                self.save_state()

            case "FSSBodySignals":
                self.state.current_system.bodies.add_body_signal(event)
                for signal in event["Signals"]:
                    match signal["Type"]:
                        case "$SAA_SignalType_Biological;": self.state.current_system.bodies.record_attribute(BodyAttribute.bios, bodyID)
                        case "$SAA_SignalType_Geological;": self.state.current_system.bodies.record_attribute(BodyAttribute.geos, bodyID)
                        case "$SAA_SignalType_Guardian;":   self.state.current_system.bodies.record_attribute(BodyAttribute.guardians, bodyID)
                        case "$SAA_SignalType_Thargoid;":   self.state.current_system.bodies.record_attribute(BodyAttribute.thargoids, bodyID)
                        case _: pass
                self.save_state()

            case "SAAScanComplete": 
                self.state.current_system.bodies.add_body_signal(event)
                self.state.current_system.bodies.record_attribute(BodyAttribute.saa_scan, bodyID)
                self.save_state()

            case "SAASignalsFound":
                self.state.current_system.bodies.add_body_signal(event)
                self.state.current_system.bodies.record_attribute(BodyAttribute.saa_signal, bodyID)
                self.save_state()

            case "FSDJump":
                self.state.previous_system = self.state.current_system
                self.state.current_system = StarSystem()
                self.state.current_system.name = event["StarSystem"]
                self.state.current_system.coordinates = (event["StarPos"][0], event["StarPos"][1], event["StarPos"][2])
                self.state.current_system.address = event["SystemAddress"]
                self.save_state()
                distance_jumped = get_distance(self.state.previous_system.coordinates, self.state.current_system.coordinates)
                self.print("Jumped " + str(round(distance_jumped, 2)) + "Ly to system: " + self.state.current_system.name)
            case _: pass

class FSSReporter(Program):
    style = Style.from_dict({
        "survey_color": "#00ffff",
        "valuable": "#6060ff",
        "biological": "#00ff00",
        "geological": "#ffff00",
    })

    SURVEY_NAME = "FSSReporter"
    SURVEY_VERSION: str = "0.0.1"
    core: CoreProgram
    report_scheduled = False

    def __init__(self, core: CoreProgram) -> None:
        super().__init__()
        self.core = core

    async def process_report(self, event: Any, delay: float):
        await asyncio.sleep(delay)
        system_name = self.core.state.current_system.name
        self.print( "╔═══════════════════════════════════════════════════════════════════════════════════</survey_color>", prefix="\n<survey_color>  ")
        self.print(f"║\tFull system scan of {self.core.state.current_system.name} complete!</survey_color>", prefix="<survey_color>  ")
        self.print( "╠═══════════════════════════════════════════════════════════════════════════════════</survey_color>", prefix="<survey_color>  ")
        self.print(f"║  Total stars:\t{len(self.core.state.current_system.bodies.get_bodies_by_attribute(BodyAttribute.star))}</survey_color>", prefix="<survey_color>  ")
        self.print(f"║  Total planets:\t{len(self.core.state.current_system.bodies.get_bodies_by_attribute(BodyAttribute.planet))}</survey_color>", prefix="<survey_color>  ")
        self.print(f"║  First discoveries:\t{len(self.core.state.current_system.bodies.get_bodies_by_attribute(BodyAttribute.first_discovery_star, BodyAttribute.first_discovery_planet))}</survey_color>", prefix="<survey_color>  ")
        bodies = self.core.state.current_system.bodies
        valuables = bodies.get_bodies_by_attribute(BodyAttribute.terraformable, BodyAttribute.earth_like_world_body, BodyAttribute.water_world_body, BodyAttribute.ammonia_world_body, sorted = True)
        if len(valuables) > 0:
            self.print("<survey_color>  ╠══</survey_color>", prefix="")
            self.print(f"  Valuable planets: {len(valuables)}</valuable>", prefix="<valuable>  ║")
            for planet in valuables:
                self.print(f"{planet["BodyName"].removeprefix(system_name)}\t\t({abbreviate_planet_type(planet["PlanetClass"])}{" + Terraformable" if planet["TerraformState"] == "Terraformable" else ""})</valuable>", prefix="<valuable>  ║\t")
           
        biologicals = bodies.get_bodies_by_attribute(BodyAttribute.bios, sorted = True)
        total_bio_count = 0
        bio_count: list[int] = []
        for bio in biologicals:
            bios = 0
            for signal in bio["Signals"]:
                bios: int = int(signal["Count"]) if signal["Type"] == "$SAA_SignalType_Biological;" else bios
            total_bio_count += bios
            bio_count.append(bios)
        if total_bio_count > 0:
            self.print("<survey_color>  ╠══</survey_color>", prefix="")
            self.print(f"  Biological signatures: {len(biologicals)} / {total_bio_count}</biological>", prefix="<biological>  ║")
            for i, planet in enumerate(biologicals):
                self.print(f"{planet["BodyName"].removeprefix(system_name)}\t\t({bio_count[i]})\tType: {abbreviate_planet_type(planet["PlanetClass"])}\tTemp: ~{int(planet["SurfaceTemperature"])}K\tAtm: {planet["AtmosphereType"]}</biological>", prefix="<biological>  ║\t")

        geologicals = bodies.get_bodies_by_attribute(BodyAttribute.geos, sorted = True)
        total_geo_count = 0
        geo_count: list[int] = []
        for geo in geologicals: 
            geos = 0
            for signal in geo["Signals"]:
                geos: int = int(signal["Count"]) if signal["Type"] == "$SAA_SignalType_Geological;" else geos
            total_geo_count += geos
            geo_count.append(geos)
        if total_geo_count > 0:
            self.print("<survey_color>  ╠══</survey_color>", prefix="")
            self.print(f"  Geological signatures: {len(geologicals)} / {total_geo_count}</geological>", prefix="<geological>  ║")
            for i, planet in enumerate(geologicals):
                self.print(f"{planet["BodyName"].removeprefix(system_name)}\t\t({geo_count[i]})\tVolcanism type: {planet["Volcanism"]}</geological>", prefix="<geological>  ║\t")
        
        self.print("<survey_color>  ╚═══════════════════════════════════════════════════════════════════════════════════</survey_color>\n", prefix="")

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:
        await super().process_event(event, tg)
        match event["event"]:
            case "FSSAllBodiesFound":
                if not self.report_scheduled:
                    self.report_scheduled = True
                    task = tg.create_task(self.process_report(event, 1))
                    if not self.caught_up: task.cancel()
            case "FSDJump":
                self.report_scheduled = False
            case _: pass

class BoxelSurvey(Program):
    style = Style.from_dict({
        "survey_color": "#ffff00",
    })

    SURVEY_NAME = "BoxelSurvey"
    SURVEY_VERSION: str = "0.0.1"
    boxel_log_file_path: Path
    system_list_file_path: Path
    system_list: list[str]
    next_system: str = ""
    core: Program

    def __init__(self, core: Program) -> None:
        super().__init__()
        self.boxel_log_file_path = self.survey_dir / Path("boxel_log")
        self.system_list_file_path = self.survey_dir / Path("boxel_survey_system_list")
        self.core = core
    
    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:
        await super().process_event(event, tg)
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
        state: dict[str, Any] = {"enabled":self.enabled, "version":self.SURVEY_VERSION}
        json.dump(state, self.state_file_path.open("w"))

    def load_state(self) -> None:
        if self.state_file_path.exists():
            state = json.load(self.state_file_path.open())
            self.enabled = state["enabled"]

class DW3DensityColumnSurvey(Program):
    style = Style.from_dict({
        "survey_color": "#ff00ff",
    })

    SURVEY_NAME = "DW3DensityColumnSurvey"
    SURVEY_VERSION: str = "0.0.1"
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

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:
        await super().process_event(event, tg)
        if self.survey_ongoing:
            match event["event"]:
                case "FSDJump":
                    current_height = self.core.state.current_system.coordinates[1]
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
    
    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:

        # TODO: Refactor this mess

        if len(arguments) > 1:
            if arguments[0] in ["dcs", "dc", "column", "densitycolumn", "densitycolumnsurvey", "dw3densitycolumnsurvey"] and self.enabled:
                galactic_height = self.core.state.current_system.coordinates[1]
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
                            self.survey_file_path = Path(self.survey_dir / str(self.core.state.current_system.name + ".tsv"))
                            self.enable()
                            self.save_state()
                            self.print("<survey_color>Started Density Column Survey from system: </survey_color>" + self.core.state.current_system.name)
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
                        await self.process_event({"event":"FSDJump"}, tg)
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
                        await super().process_user_input(arguments, tg)

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
                await super().process_user_input(arguments, tg)
                
    def process_datapoint(self, count: int, distance: float) -> None:
        current_height = self.core.state.current_system.coordinates[1]
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
            str(self.core.state.current_system) + "\t" +
            str(self.get_expected_galactic_height()) + "\t" +
            str(count) + "\t" +
            str(count + 1) + "\t" +
            str(distance) + "\t" +
            str(rho) + "\t" +
            str(self.core.state.current_system.coordinates[0]) + "\t" +
            str(self.core.state.current_system.coordinates[2]) + "\t" +
            str(self.core.state.current_system.coordinates[1])
        )
        open(self.survey_file_path, "a").write(json.dumps(datapoint) + "\n")
        self.print("<survey_color>Recorded datapoint for system: </survey_color>" + self.core.state.current_system.name)
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

