### EDSM does not receive data reliably, therefore this module will ever only be used for querying data from EDSM, not to send it there.
# For sending data to interested parties, EDDN module is used.  



import time
from src.modules import module
from src.util import EDSST_EVENTS
from prompt_toolkit.styles import Style
import asyncio
from typing import Any
import httpx
import toml
import json
from src.version import EDSST_VERSION
from pathlib import Path

config = toml.load("config.toml")


class EDSM(module.Module): 
    style = Style.from_dict({   # The KeyValue-s in this dictionary can be accessed as html tag modifiers in self.print
        "module_color": "#5bc0de",              # Example: self.print(f"<module_color>Hello World.</module_color>")
    })

    MODULE_NAME: str = "EDSM"
    MODULE_VERSION: str = "0.0.1"
    error_dump_path: Path
    #STATE_TYPE = EDSMState     # If your module has its own state class, then this has to be set to it. 
    #state: EDSMState = EDSMState() # pyright: ignore[reportIncompatibleVariableOverride]
    events_buffer: list[str] = []
    events_buffer_lock: asyncio.Lock
    responses: list[int] = []
    commander_name = config["commander_name"]
    edsm_api_key = config["edsm_api_key"]
    can_send: bool = False
    game_version: str = ""
    game_build: str = ""
    event_ignore_list: list[str] = []

    def __init__(self) -> None:
        super().__init__()
        self.error_dump_path = Path(self.module_dir / "errordump.json")
        self.event_ignore_list = self.get("https://www.edsm.net/api-journal-v1/discard", params=None)
        self.events_buffer_lock = asyncio.Lock()

    def get(self, url: str, params: Any) -> Any: 
        r = httpx.get(url, params=params)
        return r.json()

    def get_bodies_in_system(self, system_name: str):
        r = httpx.get("https://www.edsm.net/api-system-v1/bodies", params={"systemName": system_name})
        return r.json()
    
    def _add_event_to_buffer(self, event_type: str, event: str) -> bool:
        if event_type in self.event_ignore_list or event_type in EDSST_EVENTS: return False
        self.events_buffer.append(event)
        return True
    
    async def _post_events_to_edsm(self) -> bool:  # Returns whether the operation succeeded
        if self.can_send and self.events_buffer:
            async with self.events_buffer_lock:
                events = self.events_buffer[:]
                self.events_buffer.clear()
            data: dict[str, Any] = {
                "commanderName": self.commander_name,
                "apiKey": self.edsm_api_key,
                "fromSoftware": "EDSST",
                "fromSoftwareVersion": f"{EDSST_VERSION}/{self.MODULE_VERSION}",
                "fromGameVersion": f"{self.game_version}",
                "fromGameBuild": f"{self.game_build}",
                "message": [json.loads(event) for event in events]
            }
            try:
                time0 = time.time()
                async with httpx.AsyncClient() as client:
                    r = await client.post("https://www.edsm.net/api-journal-v1", json=data, timeout=30.0)
                time_elapsed = time.time() - time0
                response = r.raise_for_status().json()
            except Exception as ex:
                self.print("POST request to EDSM failed:", str(ex))
                self.events_buffer += events
                return False
            if not self._process_return_codes(response):
                self.can_send = False
                self.disable()
                try:
                    self.error_dump_path.open("w").write("\n".join(self.events_buffer))
                except:
                    self.print(f"Could not create error_dump file!")
                self.events_buffer += events
                return False
            else:
                self.print(f"Sent {len(events)} events to EDSM in {time_elapsed:.2}s.")
                return True
        return True
    
    def _process_return_codes(self, responses: dict[str, Any]) -> bool:   # Returns False if the returned code suggests to disable further data sending to edsm
        if int(responses["msgnum"]) != 100:
            self.print(f"<error>Error in bulk message!</error>")
            self.print(f"Got code <magenta>{responses["msgnum"]}, message: {responses["msg"]}")
            return False
        for i, response in enumerate(responses["events"]):
            code = int(response["msgnum"])
            match code:
                case 100 | 101 | 102 | 103 | 104: return True
                case 201 | 202 | 203 | 204 | 205 | 206 | 207 | 208 | 301 | 302 | 303 | 304: 
                    self.print(f"<error>Got code <magenta>{code}</magenta> on entry <magenta>{i}</magenta></error>")
                    self.print(f"{response["msg"]}")
                    return False
                case _:
                    self.print(f"<warning>Got code <magenta>{code}</magenta> on entry <magenta>{i}</magenta></warning>")
                    self.print(f"{response["msg"]}")
        return True

    async def process_event(self, event: Any, event_raw: str, tg: asyncio.TaskGroup) -> None:   # Events are either new journal file lines or events produced by EDSST
        await super().process_event(event, event_raw, tg)
        match event["event"]:
            case "Fileheader":
                self.game_version = str(event["gameversion"])
                self.game_build = str(event["build"])
                self.can_send = True
            case "StartJump":
                if self.caught_up:
                    tg.create_task(self._post_events_to_edsm())
                else:
                    self.events_buffer.clear()
            case "FSDJump":
                self.can_send = True
            case _: 
                self._add_event_to_buffer(event["event"], event_raw)
        

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        if arguments[0] in ["edsm", "edsmintegration", "edsmsender"]:
            match arguments[1]:
                case "send" | "push" | "post":
                    tg.create_task(self._post_events_to_edsm())
                case "displaybuffer":
                    self.print(f"Current buffer:\n{self.events_buffer}")
                case "displayignored":
                    self.print(f"Currently ignored event types:\n{self.event_ignore_list}")
                case "enable":
                    self.enable()
                case "disable":
                    self.disable()
                case _: pass