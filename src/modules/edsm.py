### EDSM does not receive data reliably, therefore this module will ever only be used for querying data from EDSM, not to send it there.
# For sending data to interested parties, EDDN module is used.  


from html import escape
from src.version import TESTING_MODE, TestingMode
from src.modules import module
from prompt_toolkit.styles import Style
import asyncio
from typing import Any
import httpx
import toml
#import json

config = toml.load("config.toml")


class EDSM(module.Module): 
    style = Style.from_dict({
        "module_color": "#5bc0de",
    })

    MODULE_NAME: str = "EDSM"
    MODULE_VERSION: str = "0.1.2"
    EXTRA_ALIASES: set[str] = set(["edsm", "edsmintegration", "edsmget"])
    responses: list[int] = []

    def __init__(self):
        super().__init__(self.EXTRA_ALIASES)
    
    async def get_system(self, system_name: str) -> Any | None:
        if not self.state.enabled:
            self.print("<warning>Can't query EDSM for a system because EDSM module is disabled!</warning>")
            return None
        r = httpx.get("https://www.edsm.net/api-v1/system", params={"systemName": system_name})
        if TESTING_MODE == TestingMode.Testing:
            self.print(escape(str(r.request.url)))
            self.print(f"{r.text}")
        return r.json()

    async def get_systems(self, list_of_systems: list[str]) -> Any | None:
        if not self.state.enabled:
            self.print("<warning>Can't query EDSM for systems because EDSM module is disabled!</warning>")
            return None
        r = httpx.get("https://www.edsm.net/api-v1/systems", params={"systemName[]": list_of_systems})
        if TESTING_MODE == TestingMode.Testing:
            self.print(escape(str(r.request.url)))
            self.print(f"{r.text}")
        return r.json()

    async def get_bodies_in_system(self, system_name: str) -> Any | None:
        if not self.state.enabled:
            self.print("<warning>Can't query EDSM for bodies in a system because EDSM module is disabled!</warning>")
            return None
        r = httpx.get("https://www.edsm.net/api-system-v1/bodies", params={"systemName": system_name})
        if TESTING_MODE == TestingMode.Testing:
            self.print(escape(str(r.request.url)))
            self.print(f"{r.text}")
        return r.json()

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:   # Events are either new journal file lines or events produced by EDSST
        await super().process_event(event, tg)
        match event["event"]:
            case _: pass

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

            