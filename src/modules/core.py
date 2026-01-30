from enum import Enum, auto
from src.modules.module import Module, ModuleState
from src.util import get_distance
import msgspec
from prompt_toolkit.styles import Style
import asyncio
from typing import Any


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


class CoreModuleState(ModuleState):
    enabled: bool = True # overloaded to set the state to True, usually can be omitted
    event_stream_enabled: bool = False
    current_system: StarSystem = msgspec.field(default_factory=StarSystem)
    previous_system: StarSystem = msgspec.field(default_factory=StarSystem)


class CoreModule(Module):
    style = Style.from_dict({
        "module_color": "#ff8000",
    })

    MODULE_NAME = "core"
    MODULE_VERSION: str = "0.0.1"
    STATE_TYPE = CoreModuleState
    commander_greeted = False
    commander_name: str = ""
    state: CoreModuleState = CoreModuleState() # pyright: ignore[reportIncompatibleVariableOverride]

    # TODO: separate out different gas giant types

    def __init__(self) -> None:
        super().__init__()

    def disable(self) -> None:
        super().disable()
        self.print("<error>Disabling the core module can have unforseen side-effects!</error>")
        self.print("<error>Consider re-enabling, unless you really know what you are doing!</error>")

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

    async def process_event(self, event: Any, event_raw: str, tg: asyncio.TaskGroup) -> None:
        await super().process_event(event, event_raw, tg)
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
                            case "Earthlike body":          self.state.current_system.bodies.record_attribute(BodyAttribute.earth_like_world_body, bodyID)
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

