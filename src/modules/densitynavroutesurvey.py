from src.modules import module
from prompt_toolkit.styles import Style
import asyncio
from typing import Any
from src.util import LOGS_DIRECTORY, get_distance
from pathlib import Path
import json


class DensityNavRouteSurvey(module.Module): 
    style = Style.from_dict({
        "module_color": "#0090de",
    })
    EXTRA_ALIASES: set[str] = set(["dnav", "navd", "densitynav", "navdensity", "navroutedensity"])
    MODULE_NAME: str = "DensityNavRouteSurvey"
    MODULE_VERSION: str = "0.0.1"
    navroute_path: Path = Path(LOGS_DIRECTORY / "NavRoute.json")
    saved_navroutes_path: Path

    def __init__(self) -> None:
        super().__init__(self.EXTRA_ALIASES)
        self.saved_navroutes_path = Path(self.module_dir / "navroutes.json")
        if not self.saved_navroutes_path.exists():
            self.saved_navroutes_path.open("w").write("")

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:
        await super().process_event(event, tg)

        match event["event"]:
            case "NavRoute":
                if self.caught_up:
                    navroute: dict[str, Any] = json.load(self.navroute_path.open())
                    if len(navroute["Route"]) < 10:
                        self.print("<yellow>Please produce a route with at least 10 jumps.</yellow>")
                        return
                    max_distance: float = 0
                    system_a_coords: tuple[float, float, float] = (float(navroute["Route"][0]["StarPos"][0]), float(navroute["Route"][0]["StarPos"][1]), float(navroute["Route"][0]["StarPos"][2]))
                    system_b_coords: tuple[float, float, float] = (float(navroute["Route"][0]["StarPos"][0]), float(navroute["Route"][0]["StarPos"][1]), float(navroute["Route"][0]["StarPos"][2]))
                    for leg in navroute["Route"]:
                        system_a_coords = system_b_coords
                        system_b_coords = (float(leg["StarPos"][0]), float(leg["StarPos"][1]), float(leg["StarPos"][2]))
                        distance = get_distance(system_a_coords, system_b_coords)
                        max_distance = distance if distance > max_distance else max_distance
                    navroute["MaxRange"] = max_distance
                    with self.saved_navroutes_path.open("a") as f:
                        json.dump(navroute, f)
                        f.write("\n")
            case _: pass

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        match arguments[1]:
            case "enable" | "start" | "listen":
                self.enable()
                self.print("<yellow>Please make sure that the following settings for the nav route algorithm are set in-game:</yellow>")
                self.print("You <green>ARE</green> in \"Fastest Routes\" mode.")
                self.print("You are <red>NOT</red> using jet cone boosts.")
                self.print("You do <red>NOT</red> have any filters set for the route.")
            case _: pass