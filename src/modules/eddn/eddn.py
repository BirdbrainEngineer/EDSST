#import time
from copy import deepcopy
from src.modules import module, core
#from src.util import EDSST_EVENTS
from prompt_toolkit.styles import Style
import asyncio
from typing import Any
import httpx
import toml
import json
from src.version import EDSST_VERSION
from pathlib import Path
from jsonschema import ValidationError, validate

config = toml.load("config.toml")

schemas_directory: Path = Path("src/modules/eddn/schemas")
eddn_journal_schema = json.load((schemas_directory / "journal-v1.0.json").open())

class EDDNState(module.ModuleState):
    hardlock: bool = False

class EDDN(module.Module): 
    style = Style.from_dict({   # The KeyValue-s in this dictionary can be accessed as html tag modifiers in self.print
        "module_color": "#5bc0de",              # Example: self.print(f"<module_color>Hello World.</module_color>")
    })

    MODULE_NAME: str = "EDDN"
    MODULE_VERSION: str = "0.0.1"
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
        match event["event"]:
            case "Docked" | "FSDJump" | "Scan" | "Location" | "SAASignalsFound" | "CarrierJump" | "CodexEntry":
                await self.post_journal_v1(event)
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

    async def post_journal_v1(self, event: dict[str, Any]) -> Any:
        event = deepcopy(event)
        
        data: dict[str, Any] = {
            "$schemaRef": "https://eddn.edcd.io/schemas/journal/1",
            "header": {
                "uploaderID":       self.core.commander_name,
                "gameversion":      self.core.game_version,
                "gamebuild":        self.core.game_build,
                "softwareName":     "EDSST",
                "softwareVersion":  f"{EDSST_VERSION}/{self.MODULE_VERSION}"
            },
            "message": {
                "timestamp":        event["timestamp"],
                "event":            event["event"],
                "horizons":         self.core.is_horizons,
                "odyssey":          self.core.is_odyssey,
                "StarSystem":       self.core.state.current_system.name,
                "StarPos":          [self.core.state.current_system.coordinates[0], self.core.state.current_system.coordinates[1], self.core.state.current_system.coordinates[2]],
                "SystemAddress":    self.core.state.current_system.address,
            }
        }
        data["message"].update(event)

        for key in data["message"]:
            if key.endswith("_Localised") or key in ("ActiveFine", "CockpitBreach", "BoostUsed", "FuelLevel", "FuelUsed", "JumpDist", "Latitude", "Longitude", "Wanted", "IsNewEntry", "NewTraitsDiscovered", "Traits", "VoucherAmount"):
                del data["message"][key]
            if key == "Factions":
                for factions_key in data[key]:
                    if factions_key in ("HappiestSystem", "HomeSystem", "MyReputation", "SquadronFaction"):
                        del data[key][factions_key]
        try:
            validate(data, eddn_journal_schema)
        except ValidationError as ex:
            self.print("<error>Tried to send an invalid message to EDDN!</error>")
            self.print(f"{data}\n\nthrew with error:\n{ex}", prefix="")
            self.print("<error>Please contact module maintainer.</error>")
            self.disable()
            return -1
        r = httpx.post("https://eddn.edcd.io:4430/upload/", json=data, timeout=15.0)
        r.raise_for_status()
        if r.status_code != 200:
            self.print(f"<error>Got back code:</error> <magenta>{r.status_code}</magenta>")
            if r.status_code == 400 or r.status_code == 426:
                self.state.hardlock = True
            try:
                self.error_dump_path.open("w").writelines(data)
            except:
                self.print("<error>Could not make error dump!</error>")
            self.disable()
        return 1


