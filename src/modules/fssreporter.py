from src.modules.core import BodyAttribute, CoreModule
from src.modules.module import Module
from src.util import abbreviate_planet_type


from prompt_toolkit.styles import Style


import asyncio
from typing import Any


class FSSReporter(Module):
    style = Style.from_dict({
        "survey_color": "#00ffff",
        "valuable": "#6060ff",
        "biological": "#00ff00",
        "geological": "#ffff00",
    })

    MODULE_NAME = "FSSReporter"
    MODULE_VERSION: str = "0.0.1"
    core: CoreModule
    report_scheduled = False

    def __init__(self, core: CoreModule) -> None:
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