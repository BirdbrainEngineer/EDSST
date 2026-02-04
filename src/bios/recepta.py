from typing import Any
from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import PlanetType, AtmosphereType#, StarType

class Recepta(Genus):
    name: str = "Recepta"
    code = "REC"
    colony_range = 150
    species: list[Species] = []

    def __init__(self):
        self.species.append(Conditivus())
        self.species.append(Deltahedronix())
        self.species.append(Umbrux())
    
    def list_possible_species(self, star_system: Bodies, planet: dict[str, Any]) -> list[Species]:
        if self.check_if_gravity_less_than(planet, 0.27):
            return super().list_possible_species(star_system, planet)
        else:
            return []


class Conditivus(Species):
    value: int = 14313700
    name: str = "Conditivus"
    code: str = "RECCON"
    planet_types: list[PlanetType] = [PlanetType.I, PlanetType.RI]
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.SO2]

class Deltahedronix(Species):
    value: int = 16202800
    name: str = "Deltahedronix"
    code: str = "RECDEL"
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.SO2]

class Umbrux(Species):
    value: int = 12934900
    name: str = "Umbrux"
    code: str = "RECUMB"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.SO2]

