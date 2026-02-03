from typing import Any
from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import PlanetType, AtmosphereType#, StarType

class Fumerola(Genus):
    name: str = "Fumerola"
    code = "FUM"
    colony_range = 100
    species: list[Species] = []

    def __init__(self):
        self.species.append(Aquatis())
        self.species.append(Carbosis())
        self.species.append(Extremus())
        self.species.append(Nitris())


class Aquatis(Species):
    value: int = 6284600
    name: str = "Aquatis"
    code: str = "FUMAQU"
    planet_types: list[PlanetType] = [PlanetType.I, PlanetType.RI]
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.ANY]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            planet_volcanism: str = planet["Volcanism"].lower()
            if "water" in planet_volcanism:
                return True
            else:
                return False
        else:
            return False

class Carbosis(Species):
    value: int = 6284600
    name: str = "Carbosis"
    code: str = "FUMCAR"
    planet_types: list[PlanetType] = [PlanetType.I, PlanetType.RI]
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.ANY]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            planet_volcanism: str = planet["Volcanism"].lower()
            if "methane" in planet_volcanism or "carbon dioxide" in planet_volcanism:
                return True
            else:
                return False
        else:
            return False

class Extremus(Species):
    value: int = 16202800
    name: str = "Extremus"
    code: str = "FUMEXT"
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.ANY]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            planet_volcanism: str = planet["Volcanism"].lower()
            if "silicate" in planet_volcanism or "iron" in planet_volcanism or "rocky" in planet_volcanism:
                return True
            else:
                return False
        else:
            return False

class Nitris(Species):
    value: int = 7500900
    name: str = "Nitris"
    code: str = "FUMNIT"
    planet_types: list[PlanetType] = [PlanetType.I, PlanetType.RI]
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.ANY]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            planet_volcanism: str = planet["Volcanism"].lower()
            if "nitrogen" in planet_volcanism or "ammonia" in planet_volcanism:
                return True
            else:
                return False
        else:
            return False

