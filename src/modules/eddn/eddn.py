from copy import deepcopy
from src.modules import module, core
from prompt_toolkit.styles import Style
import asyncio
from typing import Any
import httpx
import toml
import json
from src.version import EDSST_VERSION, TESTING_MODE, TestingMode
from pathlib import Path
from jsonschema import ValidationError, validate

config = toml.load("config.toml")

schemas_directory: Path = Path("src/modules/eddn/schemas")
eddn_journal_schema = json.load((schemas_directory / "journal-v1.0.json").open())
eddn_fssallbodiesfound_schema = json.load((schemas_directory / "fssallbodiesfound-v1.0.json").open())
eddn_fssbodysignals_schema = json.load((schemas_directory / "fssbodysignals-v1.0.json").open())
eddn_fssdiscoveryscan_schema = json.load((schemas_directory / "fssdiscoveryscan-v1.0.json").open())
eddn_scanbarycentre_schema = json.load((schemas_directory / "scanbarycentre-v1.0.json").open())


class EDDNState(module.ModuleState):
    hardlock: bool = False

class EDDN(module.Module): 
    style = Style.from_dict({   # The KeyValue-s in this dictionary can be accessed as html tag modifiers in self.print
        "module_color": "#eddd00",              # Example: self.print(f"<module_color>Hello World.</module_color>")
    })

    MODULE_NAME: str = "EDDN"
    MODULE_VERSION: str = "0.0.3"
    error_dump_path: Path
    STATE_TYPE = EDDNState     # If your module has its own state class, then this has to be set to it. 
    state: EDDNState = EDDNState()
    core: core.CoreModule
    schemas_directory: Path = Path("src/modules/eddn/schemas")


    def __init__(self, coreModule: core.CoreModule) -> None:
        super().__init__()
        self.error_dump_path = Path(self.module_dir / "errordump.json")
        self.core = coreModule
        if self.state.hardlock:
            self.print("<error>EDDN module has been locked due to previously encountering a serious problem!</error>")
            self.disable()

    async def process_event(self, event: Any, event_raw: str, tg: asyncio.TaskGroup) -> None:   # Events are either new journal file lines or events produced by EDSST
        await super().process_event(event, event_raw, tg)
        if self.state.hardlock: return
        if not self.caught_up:
            return
        else:
            match event["event"]:
                case "Docked" | "FSDJump" | "Scan" | "Location" | "SAASignalsFound" | "CarrierJump":
                    await self.post_journal_v1(event)
                case "FSSAllBodiesFound":
                    await self.post_fssallbodiesfound(event)
                case "FSSBodySignals":
                    await self.post_fssbodysignals(event)
                case "FSSDiscoveryScan":
                    await self.post_fssdiscoveryscan(event)
                case _: pass
        
    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        if arguments[0] in ["eddn", "eddnintegration", "eddnsender"]:
            if self.state.hardlock:
                self.print("<error>EDDN module has been locked due to previously encountering a serious problem.</error>")
                self.print("<warning>Check whether there is a newer version of the module available!</warning>")
                self.print("If you think the module got locked mistakenly, then to remove the lock, open:")
                self.print("edsst/modules_data/eddn/edd_state")
                self.print("and change value for <green>'hardlock'</green> to <blue>'False'</blue>. Then restart EDSST.")
                self.disable()
            match arguments[1]:
                case "enable":
                    self.enable()
                case "disable":
                    self.disable()
                case _: pass

    async def post_scanbarycentre(self, event: dict[str, Any]) -> None:
        data: dict[str, Any] = {
            "timestamp":        event["timestamp"],
            "event":            event["event"],
            "horizons":         self.core.is_horizons,
            "odyssey":          self.core.is_odyssey,
            "StarSystem":       self.core.state.current_system.name if self.core.state.current_system.name == event["StarSystem"] else None,
            "StarPos":          [self.core.state.current_system.coordinates[0], self.core.state.current_system.coordinates[1], self.core.state.current_system.coordinates[2]],
            "SystemAddress":    self.core.state.current_system.address if self.core.state.current_system.address == event["SystemAddress"] else None,
            "BodyID":           event["Progress"],
            "SemiMajorAxis":    event["BodyCount"],
            "Eccentricity":     event["NonBodyCount"],
            "OrbitalInclination":event["OrbitalInclination"],
            "Periapsis":        event["Periapsis"],
            "OrbitalPeriod":    event["OrbitalPeriod"],
            "AscendingNode":    event["AscendingNode"],
            "MeanAnomaly":      event["MeanAnomaly"],
        }
        self.validate_and_post(data, eddn_fssdiscoveryscan_schema)

    async def post_fssdiscoveryscan(self, event: dict[str, Any]) -> None:
        data: dict[str, Any] = {
            "timestamp":        event["timestamp"],
            "event":            event["event"],
            "horizons":         self.core.is_horizons,
            "odyssey":          self.core.is_odyssey,
            "SystemName":       self.core.state.current_system.name if self.core.state.current_system.name == event["SystemName"] else None,
            "StarPos":          [self.core.state.current_system.coordinates[0], self.core.state.current_system.coordinates[1], self.core.state.current_system.coordinates[2]],
            "SystemAddress":    self.core.state.current_system.address if self.core.state.current_system.address == event["SystemAddress"] else None,
            #"Progress":         event["Progress"],
            "BodyCount":        event["BodyCount"],
            "NonBodyCount":     event["NonBodyCount"],
        }
        self.validate_and_post(data, eddn_fssdiscoveryscan_schema)

    async def post_fssbodysignals(self, event: dict[str, Any]) -> None:
        data: dict[str, Any] = {
            "timestamp":        event["timestamp"],
            "event":            event["event"],
            "horizons":         self.core.is_horizons,
            "odyssey":          self.core.is_odyssey,
            "StarSystem":       self.core.state.current_system.name if event["BodyName"].startswith(self.core.state.current_system.name) else None,
            "StarPos":          [self.core.state.current_system.coordinates[0], self.core.state.current_system.coordinates[1], self.core.state.current_system.coordinates[2]],
            "SystemAddress":    self.core.state.current_system.address if self.core.state.current_system.address == event["SystemAddress"] else None,
            "BodyID":           event["BodyID"],
            "BodyName":         event["BodyName"],
            "Signals":          event["Signals"],
        }
        self.remove_localised(data)
        self.validate_and_post(data, eddn_fssbodysignals_schema)

    async def post_fssallbodiesfound(self, event: dict[str, Any]) -> None:
        data: dict[str, Any] = {
            "timestamp":        event["timestamp"],
            "event":            event["event"],
            "horizons":         self.core.is_horizons,
            "odyssey":          self.core.is_odyssey,
            "SystemName":       self.core.state.current_system.name if self.core.state.current_system.name == event["SystemName"] else None,
            "StarPos":          [self.core.state.current_system.coordinates[0], self.core.state.current_system.coordinates[1], self.core.state.current_system.coordinates[2]],
            "SystemAddress":    self.core.state.current_system.address if self.core.state.current_system.address == event["SystemAddress"] else None,
            "Count":            event["Count"],
        }
        self.validate_and_post(data, eddn_fssallbodiesfound_schema)

    async def post_journal_v1(self, event: dict[str, Any]) -> None:
        event = deepcopy(event)
        data: dict[str, Any] = {
            "timestamp":        event["timestamp"],
            "event":            event["event"],
            "horizons":         self.core.is_horizons,
            "odyssey":          self.core.is_odyssey,
            "StarSystem":       self.core.state.current_system.name if "StarSystem" not in event else self.core.state.current_system.name if self.core.state.current_system.name == event["StarSystem"] else None,
            "StarPos":          [self.core.state.current_system.coordinates[0], self.core.state.current_system.coordinates[1], self.core.state.current_system.coordinates[2]],
            "SystemAddress":    self.core.state.current_system.address if self.core.state.current_system.address == event["SystemAddress"] else None,
        }
        event.update(data)
        data = event
        self.remove_localised(data)
        self.try_remove_keys(data, ["ActiveFine", "CockpitBreach", "BoostUsed", "FuelLevel", "FuelUsed", "JumpDist", "Latitude", "Longitude", "Wanted", "IsNewEntry", "NewTraitsDiscovered", "Traits", "VoucherAmount"])
        if "Factions" in data:
            self.try_remove_keys(data["Factions"], ["HappiestSystem", "HomeSystem", "MyReputation", "SquadronFaction"])
        self.validate_and_post(data, eddn_journal_schema)
        

    def validate_and_post(self, message_data: dict[str, Any], schema: Any) -> None:
        schema_ref = schema["id"].rstrip("#")
        data: dict[str, Any] = {
            "$schemaRef": schema_ref if TESTING_MODE == TestingMode.Release else f"{schema_ref}/test",
            "header": {
                "uploaderID":       self.core.commander_name,
                "gameversion":      self.core.game_version,
                "gamebuild":        self.core.game_build,
                "softwareName":     "EDSST",
                "softwareVersion":  f"{EDSST_VERSION}/{self.MODULE_VERSION}"
            },
            "message": message_data
        }
        try:
            validate(data, schema)
        except ValidationError as ex:
            self.print("<error>Tried to send an invalid message to EDDN!</error>")
            self.print(f"{data}\n\nthrew with error:\n{ex}", prefix="")
            self.print("<error>Please contact module maintainer.</error>")
            self.disable()
        r = httpx.post("https://eddn.edcd.io:4430/upload/", json=data, timeout=15.0)
        r.raise_for_status()
        if TESTING_MODE == TestingMode.Testing:
            self.print(f"<blue>Testing</blue>: With event <mint>{data["message"]["event"]}</mint> on <bright_blue>{data["$schemaRef"].removeprefix("https://eddn.edcd.io/schemas/")}</bright_blue> got response code <magenta>{r.status_code}</magenta> - {r.text}")
        if r.status_code != 200:
            self.print(f"<error>Got back code:</error> <magenta>{r.status_code}</magenta>")
            if r.status_code == 400 or r.status_code == 426:
                if TESTING_MODE == TestingMode.Release:
                    self.state.hardlock = True
            try:
                self.error_dump_path.open("w").writelines(data)
            except:
                self.print("<error>Could not make error dump!</error>")
            self.disable()

    def remove_localised(self, data: dict[str, Any]) -> None:
        delete_keys: list[str] = []
        for key in data:

            if key.endswith("_Localised"):
                delete_keys.append(key)
            elif isinstance(data[key], dict):
                self.remove_localised(data[key])
            elif isinstance(data[key], list):
                for item in data[key]:
                    if isinstance(item, dict):
                        self.remove_localised(item)
        
        for key in delete_keys:
            del data[key]

    def try_remove_keys(self, data: dict[str, Any], keys: list[str]) -> None:
        for key in keys:
            if key in data:
                del data[key]
