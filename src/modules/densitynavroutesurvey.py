from dataclasses import dataclass
from src.modules import module
from prompt_toolkit.styles import Style
import asyncio
from typing import Any
from src.util import LOGS_DIRECTORY, get_distance
from pathlib import Path
import json
from enum import Enum
import re

FSD_REGEX = re.compile(r".*_size(\d)_class(\d)")

class FSDBooster(Enum):
    NONE = 0.0
    H1 = 4.0
    H2 = 6.0
    H3 = 7.75
    H4 = 9.25
    H5 = 10.5

@dataclass
class FSD_Attribute():
    power_factor: float
    fuel_multiplier: float
    max_fuel: float
    optimal_mass: float

FSD_ATTRIBUTES: dict[str, FSD_Attribute] = { # power constant, fuel multiplier, max fuel per jump, optimal mass
    "E2_SCO": FSD_Attribute(2.0, 0.008, 0.6, 60),
    "D2_SCO": FSD_Attribute(2.0, 0.012, 0.6, 90),
    "C2_SCO": FSD_Attribute(2.0, 0.012, 0.9, 90),
    "B2_SCO": FSD_Attribute(2.0, 0.012, 0.9, 90),
    "A2_SCO": FSD_Attribute(2.0, 0.013, 1.0, 100),
    "E3_SCO": FSD_Attribute(2.15, 0.008, 1.2, 100),
    "D3_SCO": FSD_Attribute(2.15, 0.012, 1.8, 150),
    "C3_SCO": FSD_Attribute(2.15, 0.012, 1.8, 150),
    "B3_SCO": FSD_Attribute(2.15, 0.012, 1.8, 150),
    "A3_SCO": FSD_Attribute(2.15, 0.013, 1.9, 167),
    "E4_SCO": FSD_Attribute(2.3, 0.008, 2.0, 350),
    "D4_SCO": FSD_Attribute(2.3, 0.012, 3.0, 525),
    "C4_SCO": FSD_Attribute(2.3, 0.012, 3.0, 525),
    "B4_SCO": FSD_Attribute(2.3, 0.012, 3.0, 525),
    "A4_SCO": FSD_Attribute(2.3, 0.013, 3.2, 585),
    "E5_SCO": FSD_Attribute(2.45, 0.008, 3.3, 700),
    "D5_SCO": FSD_Attribute(2.45, 0.012, 5.0, 1050),
    "C5_SCO": FSD_Attribute(2.45, 0.012, 5.0, 1050),
    "B5_SCO": FSD_Attribute(2.45, 0.012, 5.0, 1050),
    "A5_SCO": FSD_Attribute(2.45, 0.013, 5.2, 1175),
    "E6_SCO": FSD_Attribute(2.6, 0.008, 5.3, 1200),
    "D6_SCO": FSD_Attribute(2.6, 0.012, 8.0, 1800),
    "C6_SCO": FSD_Attribute(2.6, 0.012, 8.0, 1800),
    "B6_SCO": FSD_Attribute(2.6, 0.012, 8.0, 1800),
    "A6_SCO": FSD_Attribute(2.6, 0.013, 8.3, 2000),
    "E7_SCO": FSD_Attribute(2.75, 0.008, 8.5, 1800),
    "D7_SCO": FSD_Attribute(2.75, 0.012, 12.8, 2700),
    "C7_SCO": FSD_Attribute(2.75, 0.012, 12.8, 2700),
    "B7_SCO": FSD_Attribute(2.75, 0.012, 12.8, 2700),
    "A7_SCO": FSD_Attribute(2.75, 0.013, 13.1, 3000),
    "E8_SCO": FSD_Attribute(2.9, 0.008, 13.6, 2800),
    "D8_SCO": FSD_Attribute(2.9, 0.012, 20.4, 4200),
    "C8_SCO": FSD_Attribute(2.9, 0.012, 20.4, 4200),
    "B8_SCO": FSD_Attribute(2.9, 0.012, 20.4, 4200),
    "A8_SCO": FSD_Attribute(2.9, 0.013, 20.7, 4670),
    "A8_SCO_MK2": FSD_Attribute(2.9, 0.13, 20.7, 4670),     #The mk2 really messes up the fuel equation., ..
    "E2": FSD_Attribute(2.0, 0.011, 0.6, 48),
    "D2": FSD_Attribute(2.0, 0.01, 0.6, 54),
    "C2": FSD_Attribute(2.0, 0.008, 0.6, 60),
    "B2": FSD_Attribute(2.0, 0.01, 0.8, 75),
    "A2": FSD_Attribute(2.0, 0.12, 0.9, 90),
    "E3": FSD_Attribute(2.15, 0.011, 1.2, 80),
    "D3": FSD_Attribute(2.15, 0.01, 1.2, 90),
    "C3": FSD_Attribute(2.15, 0.008, 1.2, 100),
    "B3": FSD_Attribute(2.15, 0.01, 1.5, 125),
    "A3": FSD_Attribute(2.15, 0.12, 1.8, 150),
    "E4": FSD_Attribute(2.3, 0.011, 2.0, 280),
    "D4": FSD_Attribute(2.3, 0.01, 2.0, 315),
    "C4": FSD_Attribute(2.3, 0.008, 2.0, 350),
    "B4": FSD_Attribute(2.3, 0.01, 2.5, 438),
    "A4": FSD_Attribute(2.3, 0.12, 3.0, 525),
    "E5": FSD_Attribute(2.45, 0.011, 3.3, 560),
    "D5": FSD_Attribute(2.45, 0.01, 3.3, 630),
    "C5": FSD_Attribute(2.45, 0.008, 3.3, 700),
    "B5": FSD_Attribute(2.45, 0.01, 4.1, 875),
    "A5": FSD_Attribute(2.45, 0.12, 5.0, 1050),
    "E6": FSD_Attribute(2.6, 0.011, 5.3, 960),
    "D6": FSD_Attribute(2.6, 0.01, 5.3, 1080),
    "C6": FSD_Attribute(2.6, 0.008, 5.3, 1200),
    "B6": FSD_Attribute(2.6, 0.01, 6.6, 1500),
    "A6": FSD_Attribute(2.6, 0.12, 8.0, 1800),
    "E7": FSD_Attribute(2.75, 0.011, 8.5, 1440),
    "D7": FSD_Attribute(2.75, 0.01, 8.5, 1620),
    "C7": FSD_Attribute(2.75, 0.008, 8.5, 1800),
    "B7": FSD_Attribute(2.75, 0.01, 10.6, 2250),
    "A7": FSD_Attribute(2.75, 0.12, 12.8, 2700),
}

class DensityNavRouteSurvey(module.Module): 
    style = Style.from_dict({
        "module_color": "#0090de",
    })
    EXTRA_ALIASES: set[str] = set(["dnav", "navd", "densitynav", "navdensity", "navroutedensity"])
    MODULE_NAME: str = "DensityNavRouteSurvey"
    MODULE_VERSION: str = "0.0.2"
    navroute_path: Path = Path(LOGS_DIRECTORY / "NavRoute.json")
    saved_navroutes_path: Path
    jump_range: float = 0
    fsd_attributes: FSD_Attribute = FSD_Attribute(0, 0, 0, 0)
    guardian_booster: FSDBooster = FSDBooster.NONE
    fsd_optimised_mass = 0
    ship_unladen_mass = 0
    cargo_onboard: int = 0
    max_fuel: float = 0
    ABSOLUTE_MAX_POSSIBLE_JUMP_DISTANCE: float = 100
    

    def __init__(self) -> None:
        super().__init__(self.EXTRA_ALIASES)
        self.saved_navroutes_path = Path(self.module_dir / "navroutes.json")
        if not self.saved_navroutes_path.exists():
            self.saved_navroutes_path.open("w").write("")

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:
        await super().process_event(event, tg)

        match event["event"]:
            #case "Cargo":
            #    if event["Vessel"] == "Ship":
            #        self.cargo_onboard = int(event["Count"])
            #case "Loadout":
            #    fsd, booster = self.get_fsd_capabilities(event)
            #    if not fsd or not booster:
            #        self.print("Unrecoverable error when determining jump capabilities.")
            #        self.disable()
            #        return
            #    self.fsd_attributes = fsd
            #    self.guardian_booster = booster
            #    self.max_fuel = float(event["FuelCapacity"]["Main"]) + float(event["FuelCapacity"]["Reserve"])
            #    self.ship_unladen_mass = float(event["UnladenMass"])

            case "NavRoute":
                if self.caught_up:
                    navroute: dict[str, Any] = json.load(self.navroute_path.open())
                    if len(navroute["Route"]) < 10:
                        self.print("<yellow>Please produce a route with at least 10 jumps.</yellow>")
                        return
                    max_distance = 0
                    system_a_coords: tuple[float, float, float] = (float(navroute["Route"][0]["StarPos"][0]), float(navroute["Route"][0]["StarPos"][1]), float(navroute["Route"][0]["StarPos"][2]))
                    system_b_coords: tuple[float, float, float] = (float(navroute["Route"][0]["StarPos"][0]), float(navroute["Route"][0]["StarPos"][1]), float(navroute["Route"][0]["StarPos"][2]))
                    for leg in navroute["Route"]:
                        system_a_coords = system_b_coords
                        system_b_coords = (float(leg["StarPos"][0]), float(leg["StarPos"][1]), float(leg["StarPos"][2]))
                        distance = get_distance(system_a_coords, system_b_coords)
                        if distance > self.ABSOLUTE_MAX_POSSIBLE_JUMP_DISTANCE:
                            self.print("Detected a boosted jump, rejecting route! Please disable jet cone boosts!")
                            return
                        if distance > max_distance: max_distance = distance # The max distance needs to be taken this way because sometimes the route planner makes you jump a larger distance than your ship can jump fully fuelled
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
            case "disable" | "stop" | "deafen":
                self.disable()
            case _: pass

    #def get_current_max_jump_range(self) -> float:
    #    ship_mass = self.ship_unladen_mass + self.fsd_attributes.max_fuel
    #    self.jump_range = self.fsd_optimised_mass/
    #    return 0

    def get_fsd_capabilities(self, loadout_event: dict[str, Any]) -> tuple[FSD_Attribute, FSDBooster] | tuple[None, None]:
        if "Ship" in loadout_event:
            fsd_variant: FSD_Attribute | None = None
            booster: FSDBooster | None = FSDBooster.NONE
            if loadout_event["Ship"]:
                for module in loadout_event["Modules"]:
                    if module["Slot"] == "FrameShiftDrive":
                        deep_charge: bool = False
                        key: str = ""
                        match = FSD_REGEX.match(module["Item"])
                        if match:
                            size, class_ = match.groups()
                            match class_:
                                case "1": key = "E"
                                case "2": key = "D"
                                case "3": key = "C"
                                case "4": key = "B"
                                case "5": key = "A"
                                case _:
                                    self.print("Something went wrong while trying to determine fsd capabilities.")
                                    self.disable()
                                    return (None, None)
                            key = key + str(size)
                            if "overcharge" in module["Item"]: key = key + "_SCO"
                            if "mk2" in module["Item"].lower(): key = key + "_MK2"
                            fsd_variant = FSD_Attribute(FSD_ATTRIBUTES[key].power_factor,FSD_ATTRIBUTES[key].fuel_multiplier, FSD_ATTRIBUTES[key].max_fuel, FSD_ATTRIBUTES[key].optimal_mass)
                            if "Engineering" in module:
                                if "Modifiers" in module["Engineering"]:
                                    for modifier in module["Engineering"]["Modifiers"]:
                                        if modifier["Label"] == "FSDOptimalMass":
                                            fsd_variant.optimal_mass = float(modifier["Value"])
                                if "ExperimentalEffect_Localised" in module["Engineering"]:
                                    if module["Engineering"]["ExperimentalEffect_Localised"] in ("Deep Charge", "Mass Manager", ""):
                                        if module["Engineering"]["ExperimentalEffect_Localised"] == "Deep Charge":
                                            deep_charge = True
                                    else:
                                        self.print("Could not figure out ship's maximum jump range because can't read the experimental effect applied on the fsd")
                                        self.disable()
                                        return (None, None)
                            if deep_charge: fsd_variant.max_fuel = fsd_variant.max_fuel + (fsd_variant.max_fuel * 0.1)
                        else:
                            self.print("Found an invalid fsd name in journal file.")
                            self.disable()
                            return (None, None)
                    if "Item" in module:
                        if "guardianfsdbooster" in module["Item"]:
                            if "size1" in module["Item"]: booster = FSDBooster.H1
                            elif "size2" in module["Item"]: booster = FSDBooster.H2
                            elif "size3" in module["Item"]: booster = FSDBooster.H3
                            elif "size4" in module["Item"]: booster = FSDBooster.H4
                            elif "size5" in module["Item"]: booster = FSDBooster.H5
                            else:
                                self.print("Retrieved invalid sized guardian booster!")
                                self.disable()
                                return (None, None)
            if fsd_variant and booster:
                return (fsd_variant, booster)
            else:
                self.print("Something went wrong when determining jump capabilities.")
                self.disable()
                return (None, None)
        else:
            return (None, None)
        