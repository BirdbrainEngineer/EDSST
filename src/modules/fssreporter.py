from src.modules.core import BodyAttribute, CoreModule
from src.modules.module import Module, ModuleState
from src.util import abbreviate_planet_type
from prompt_toolkit.styles import Style
import asyncio
from typing import Any
from src.bios import taxon, species

class FSSReporterState(ModuleState):
    display_verbose: bool = False

class FSSReporter(Module):
    style = Style.from_dict({
        "module_color": "#00ffff",
        "valuable": "#6060ff bold",
        "biological": "#00a000 bold",
        "bio": "#00ff80",
        "geological": "#ffff00 bold",
        "module_bold": "#00ffff bold"
    })

    MODULE_NAME = "FSSReporter"
    MODULE_VERSION: str = "0.1.0"
    EXTRA_ALIASES: set[str] = set(["fss", "scanreport"])
    STATE_TYPE = FSSReporterState
    core: CoreModule
    report_scheduled = False
    state: FSSReporterState = FSSReporterState()

    def __init__(self, core: CoreModule) -> None:
        super().__init__(self.EXTRA_ALIASES)
        self.core = core

    async def process_report(self, delay: float):
        await asyncio.sleep(delay)
        system_name = self.core.state.current_system.name
        num_stars = str(len(self.core.state.current_system.bodies.get_bodies_by_attribute(BodyAttribute.star)))
        num_planets = str(len(self.core.state.current_system.bodies.get_bodies_by_attribute(BodyAttribute.planet)))
        first_discoveries = str(len(self.core.state.current_system.bodies.get_bodies_by_attribute(BodyAttribute.first_discovery_star, BodyAttribute.first_discovery_planet)))
        self.print( "╔═══════════════════════════════════════════════════════════════════════════════════</module_color>", prefix="\n<module_color>  ")
        self.print(f"║\t</module_color>{"<green_bold>Full</green_bold>" if self.report_scheduled else "<yellow_bold>Partial</yellow_bold>"} <module_bold>system scan of {self.core.state.current_system.name} {"complete!" if self.report_scheduled else ""}</module_bold>", prefix="<module_color>  ")
        self.print( "╠═══════════════════════════════════════════════════════════════════════════════════</module_color>", prefix="<module_color>  ")
        self.print(f"║  Stars: {num_stars:5}Planets: {num_planets:5}First discoveries: {first_discoveries}</module_color>", prefix="<module_color>  ")
        bodies = self.core.state.current_system.bodies
        valuables = bodies.get_bodies_by_attribute(BodyAttribute.terraformable, BodyAttribute.earth_like_world_body, BodyAttribute.water_world_body, BodyAttribute.ammonia_world_body, sorted = True)
        if len(valuables) > 0:
            self.print("<module_color>  ╠══</module_color>", prefix="")
            self.print(f"  Valuable planets: {len(valuables)}</valuable>", prefix="<valuable>  ║")
            for planet in valuables:
                self.print(f"{planet["BodyName"].removeprefix(system_name):13}({abbreviate_planet_type(planet["PlanetClass"])}{" + Terraformable" if planet["TerraformState"] == "Terraformable" else ""})</valuable>", prefix="<valuable>  ║\t")

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
            self.print("<module_color>  ╠══</module_color>", prefix="")
            self.print(f"  Biological signatures: {len(biologicals)} / {total_bio_count}</biological>", prefix="<biological>  ║")
            for i, planet in enumerate(biologicals):
                planet_bio_count: str = f"({bio_count[i]})"
                surface_temp = int(planet["SurfaceTemperature"])
                atmosphere_type = str(planet["AtmosphereType"])
                planet_type = abbreviate_planet_type(planet["PlanetClass"])
                bios_worth = self.get_estimated_bio_worth(planet, bio_count[i])
                min_value: float = float(round(bios_worth[0] / 1000000, ndigits=1))
                max_value: float = float(round(bios_worth[1] / 1000000, ndigits=1))
                average_value: float = float(round(bios_worth[2] / 1000000, ndigits=1))
                self.print(f"{planet["BodyName"].removeprefix(system_name):13}{planet_bio_count:7}{f"{min_value}M - {max_value}M | {average_value}M":28}{planet_type:8}{str(str(surface_temp)+"K"):10}{atmosphere_type}</biological>", prefix="<biological>  ║\t")
                if self.state.display_verbose:
                    organisms: list[str] = []
                    for genus in bios_worth[3]:
                        for species in genus:
                            organisms.append(f"{species.code} {round(float(species.value / 1000000), ndigits=1)}M")
                    output: str = ""
                    for j in range(len(organisms)):
                        output = f"{output}<bio>{organisms[j]:16}</bio>"
                        if (j + 1) % 6 == 0 and len(organisms) > (j + 1):
                            output = str(output + "\n  <biological>║</biological>\t\t")
                    self.print(f"</biological>{output}", prefix="<biological>  ║\t\t")

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
            self.print("<module_color>  ╠══</module_color>", prefix="")
            self.print(f"  Geological signatures: {len(geologicals)} / {total_geo_count}</geological>", prefix="<geological>  ║")
            for i, planet in enumerate(geologicals):
                self.print(f"{planet["BodyName"].removeprefix(system_name):13}({str(geo_count[i])+")":7}Volcanism type: {planet["Volcanism"]}</geological>", prefix="<geological>  ║\t")

        self.print("<module_color>  ╚═══════════════════════════════════════════════════════════════════════════════════</module_color>\n", prefix="")

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:
        await super().process_event(event, tg)
        match event["event"]:
            case "FSSAllBodiesFound":
                if not self.report_scheduled:
                    self.report_scheduled = True
                    task = tg.create_task(self.process_report(1))
                    if not self.caught_up: task.cancel()
            case "FSDJump":
                self.report_scheduled = False
            case _: pass

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        await super().process_user_input(arguments, tg)
        match arguments[1]:
            case "report":
                await self.process_report(0.01)
            case "more":
                if arguments[2]:
                    if arguments[2] == "verbose":
                        self.state.display_verbose = True
                        self.print("Reports are now <yellow>more</yellow> verbose!")
                        self.save_state()
            case "less":
                if arguments[2]:
                    if arguments[2] == "verbose":
                        self.state.display_verbose = False
                        self.print("Reports are now <yellow>less</yellow> verbose!")
                        self.save_state()
            case _: pass

    def get_estimated_bio_worth(self, planet: dict[str, Any], num_signatures: int) -> tuple[int, int, int, list[list[species.Species]]]:
        valid_species: list[list[species.Species]] = []
        maximum_values: list[int] = []
        minimum_values: list[int] = []
        average_values: list[int] = []
        for genus in taxon:
            valid_species_in_genus = genus.list_possible_species(self.core.state.current_system.bodies, planet)
            if valid_species_in_genus:
                valid_species.append(valid_species_in_genus)
        for genus in valid_species:
            max_value = 0
            min_value = genus[0].value
            average_value = 0
            for species in genus:
                if species.value > max_value: max_value = species.value
                if species.value < min_value: min_value = species.value
                average_value += species.value
            average_value = int(average_value / len(genus))
            maximum_values.append(max_value)
            minimum_values.append(min_value)
            average_values.append(average_value)
        maximum_values.sort(reverse=True)
        minimum_values.sort()
        total_minimum_value = sum(minimum_values[:num_signatures])
        total_maximum_value = sum(maximum_values[:num_signatures])
        total_average_value = int(sum(average_values) / len(average_values))
        
        return (total_minimum_value, total_maximum_value, total_average_value, valid_species)