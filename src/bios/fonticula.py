from typing import Any
from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType, PlanetType#StarType, 

class Fonticula(Genus):
    name: str = "Fonticula"
    code = "FON"
    colony_range = 500
    species: list[Species] = []

    def __init__(self):
        self.species.append(Campestris())
        self.species.append(Digitos())
        self.species.append(Fluctus())
        self.species.append(Lapida())
        self.species.append(Segmentatus())
        self.species.append(Upupam())
    
    def list_possible_species(self, star_system: Bodies, planet: dict[str, Any]) -> list[Species]:
        if self.check_if_gravity_less_than(planet, 0.29):
            return super().list_possible_species(star_system, planet)
        else:
            return []


class Campestris(Species):
    value: int = 1000000
    name: str = "Campestris"
    code: str = "FONCAM"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.Ar, AtmosphereType.Ar_R]
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.RI, PlanetType.I]

class Digitos(Species):
    value: int = 1804100
    name: str = "Digitos"
    code: str = "FONDIG"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CH4, AtmosphereType.CH4_R]
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.RI, PlanetType.I]

class Fluctus(Species):
    value: int = 16777215
    name: str = "Fluctus"
    code: str = "FONFLU"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.O2]
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.RI, PlanetType.I]

class Lapida(Species):
    value: int = 3111000
    name: str = "Lapida"
    code: str = "FONLAP"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.N2]
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.RI, PlanetType.I]

class Segmentatus(Species):
    value: int = 19010800
    name: str = "Segmentatus"
    code: str = "FONSEG"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.Ne, AtmosphereType.Ne_R]

class Upupam(Species):
    value: int = 5727600
    name: str = "Upupam"
    code: str = "FONUPU"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.Ar_R]
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.RI, PlanetType.I]