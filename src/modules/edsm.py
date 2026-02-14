### EDSM does not receive data reliably, therefore this module will ever only be used for querying data from EDSM, not to send it there.
# For sending data to interested parties, EDDN module is used.  


from html import escape
import json
from src.version import TESTING_MODE, TestingMode, EDSST_VERSION
from src.modules import module
from prompt_toolkit.styles import Style
import asyncio
from typing import Any
import httpx
import toml
from src.modules.core import CoreModule

config = toml.load("config.toml")
api_key = config.get("edsm_api_key", None)
edsm_commander_name = config.get("edsm_commander_name", None)


class EDSM(module.Module): 
    style = Style.from_dict({
        "module_color": "#5bc0de",
    })

    MODULE_NAME: str = "EDSM"
    MODULE_VERSION: str = "0.2.0"
    EXTRA_ALIASES: set[str] = set(["edsm", "edsmintegration", "edsmget"])
    ignore_list: list[str] = []
    responses: list[int] = []
    core: CoreModule
    httpx_client: httpx.AsyncClient
    

    def __init__(self, core: CoreModule):
        super().__init__(self.EXTRA_ALIASES)
        self.core = core
        self.httpx_client = httpx.AsyncClient(timeout=5.0)
        if api_key is None or edsm_commander_name is None:
            self.print("<warning>EDSM API key or commander name not found in config.toml!</warning>")
        if not self.state.enabled:
            self.enable()
        try:
            r = httpx.get("https://www.edsm.net/api-journal-v1/discard", timeout=5.0)
            r.raise_for_status()
        except httpx.TimeoutException:
            self.print(f"<warning>Could not GET EDSM ignore list, request timed out.</warning>")
            self.disable()
            return
        except httpx.RequestError as exc:
            self.print(f"<error>Could not GET EDSM ignore list, an error occurred: {str(exc)}</error>")
            self.disable()
            return
        else:
            self.ignore_list = r.json()
            if TESTING_MODE == TestingMode.Testing:
                self.print(f"EDSM ignore list: {str(self.ignore_list)}")
        if api_key is None or edsm_commander_name is None or api_key == "" or edsm_commander_name == "":
            self.print(f"<error>Can not POST to EDSM because API key or commander name is not set in config.toml!</error>")
            self.disable()


    async def post(self, event: dict[str, Any]) -> None:
        if api_key is None or edsm_commander_name is None or api_key == "" or edsm_commander_name == "":
            return
        if not self.state.enabled:
            self.print(f"<error>Could not send event: {event['event']}, EDSM disabled!</error>")
            return
        if not self.ignore_list:
            self.print(f"<error>Could not send event: {event['event']}, EDSM ignore list is empty!</error>")
            self.disable()
            return
        if event["event"] in self.ignore_list:
            if TESTING_MODE == TestingMode.Testing:
                self.print(f"<warning>Not sending event: {event['event']} to EDSM because it's in the ignore list.</warning>")
            return
        coordinates = self.core.state.current_system.coordinates
        data: dict[str, Any] = {
            "commanderName": edsm_commander_name,
            "apiKey": api_key,
            "fromSoftware": "EDSST",
            "fromSoftwareVersion": f"{EDSST_VERSION}/{self.MODULE_VERSION}",
            "fromGameVersion": self.core.game_version,
            "fromGameBuild": self.core.game_build,
            "message": json.dumps(event),
            "_systemAddress": self.core.state.current_system.address,
            "_systemName": self.core.state.current_system.name,
            "_systemCoordinates": [coordinates[0], coordinates[1], coordinates[2]],
            "_marketId": None,
            "_stationName": None,
            "_shipId": None
        }
        try:
            if TESTING_MODE == TestingMode.Testing:
                self.print(f"Posting event: {event['event']} to EDSM...")
            r = await self.httpx_client.post(url = f"https://www.edsm.net/api-journal-v1", data=data)
        except httpx.TimeoutException:
            self.print(f"<error>Could not POST to EDSM, request timed out.</error>")
            return
        if r.status_code != 200:
            self.print(f"<error>Something went wrong when trying to POST {event['event']} to EDSM, status code: {r.status_code}, response: {r.text}</error>")
            self.print(f"Response: {r.text}")
            self.disable()
            return
        else:
            response = json.loads(r.text)
            if response["msgnum"] != 100:
                self.print(f"EDSM returned code {response["msgnum"]} - {response["msg"]}")
                return
            for message in response["events"]:
                if message["msgnum"] != 100:
                    self.print(f"EDSM returned code {message["msgnum"]} - {message["msg"]}")
                    return
            if TESTING_MODE == TestingMode.Testing:
                self.print(f"Successfully POSTed event: {event['event']} to EDSM")

    
    async def get_system(self, system_name: str) -> Any | None:
        try:
            r = httpx.get("https://www.edsm.net/api-v1/system", params={"systemName": system_name})
            r.raise_for_status()
        except:
            self.print(f"<error>Could not GET system {system_name} from EDSM.</error>")
            return None
        if TESTING_MODE == TestingMode.Testing:
            self.print(escape(str(r.request.url)))
            self.print(f"{r.text}")
        return r.json()

    async def get_systems(self, list_of_systems: list[str]) -> Any | None:
        try:
            r = httpx.get("https://www.edsm.net/api-v1/systems", params={"systemName[]": list_of_systems})
            r.raise_for_status()
        except:
            self.print(f"<error>Could not GET systems {list_of_systems} from EDSM.</error>")
            return None
        if TESTING_MODE == TestingMode.Testing:
            self.print(escape(str(r.request.url)))
            self.print(f"{r.text}")
        return r.json()

    async def get_bodies_in_system(self, system_name: str) -> Any | None:
        try:
            r = httpx.get("https://www.edsm.net/api-system-v1/bodies", params={"systemName": system_name})
            r.raise_for_status()
        except:
            self.print(f"<error>Could not GET bodies in system {system_name} from EDSM.</error>")
            return None
        if TESTING_MODE == TestingMode.Testing:
            self.print(escape(str(r.request.url)))
            self.print(f"{r.text}")
        return r.json()

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None: 
        await super().process_event(event, tg)
        match event["event"]:
            case _: 
                if self.caught_up:
                    if event["event"] != "CaughtUp": 
                        if self.state.enabled:
                            tg.create_task(self.post(event))
                

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        await super().process_user_input(arguments, tg)
        if len(arguments) < 2: return
        match arguments[1]:
            case "get" | "load" | "getsystem" | "loadsystem":
                system_name = " ".join(arguments[2:])
                response = await self.get_system(system_name)
                if TESTING_MODE == TestingMode.Testing: 
                    self.print(f"{str(response)}")
                else:
                    self.print(f"{str(response)}")
            case _: pass

            