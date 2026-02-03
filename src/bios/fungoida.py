from typing import Any
from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType#, PlanetType, StarType

class Fungoida(Genus):
    name: str = "Fungoida"
    code = "FUN"
    colony_range = 300
    species: list[Species] = []

    def __init__(self):
        self.species.append(Bullarum())
        self.species.append(Gelata())
        self.species.append(Setisis())
        self.species.append(Stabitis())


class Bullarum(Species):
    value: int = 3703200
    name: str = "Bullarum"
    code: str = "FUNBUL"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.Ar, AtmosphereType.Ar_R]

class Gelata(Species):
    value: int = 3330300
    name: str = "Gelata"
    code: str = "FUNGEL"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R, AtmosphereType.H2O]
    min_max_temperature: tuple[int, int] = (180, 195)

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            return True
        else:
            if planet["AtmosphereType"] == "Water":
                return True
            else:
                return False

class Setisis(Species):
    value: int = 1670100
    name: str = "Setisis"
    code: str = "FUNSET"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3, AtmosphereType.CH4, AtmosphereType.CH4_R]

class Stabitis(Species):
    value: int = 2680300
    name: str = "Stabitis"
    code: str = "FUNSTA"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R, AtmosphereType.H2O]
    min_max_temperature: tuple[int, int] = (180, 195)

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            return True
        else:
            if planet["AtmosphereType"] == "Water":
                return True
            else:
                return False