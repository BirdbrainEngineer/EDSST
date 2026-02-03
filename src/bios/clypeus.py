from typing import Any
from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import distance_from_parent_ls
from src.util import AtmosphereType, PlanetType#, StarType

class Clypeus(Genus):
    name: str = "Clypeus"
    code = "CLY"
    colony_range = 150
    species: list[Species] = []

    def __init__(self):
        self.species.append(Lacrimam())
        self.species.append(Margaritus())
        self.species.append(Speculumi())

    def list_possible_species(self, star_system: Bodies, planet: dict[str, Any]) -> list[Species]:
        if self.check_if_gravity_less_than(planet, 0.27):
            if PlanetType(planet["PlanetClass"]) in [PlanetType.HMC, PlanetType.R]:
                return super().list_possible_species(star_system, planet)
            else:
                return []
        else:
            return []
        

class Lacrimam(Species):
    value: int = 8418000
    name: str = "Lacrimam"
    code: str = "CLYLAC"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.H2O]
    min_max_temperature: tuple[int, int] = (190, 190)
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

class Margaritus(Species):
    value: int = 11873200
    name: str = "Margaritus"
    code: str = "CLYMAR"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.H2O]
    min_max_temperature: tuple[int, int] = (190, 190)
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

class Speculumi(Species):
    value: int = 16202800
    name: str = "Speculumi"
    code: str = "CLYSPE"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.H2O]
    min_max_temperature: tuple[int, int] = (190, 190)
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if distance_from_parent_ls(planet["SemiMajorAxis"], planet["Eccentricity"], planet["MeanAnomaly"]) > 2500:
            return True
        else:
            return False