from typing import Any
from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType, PlanetType#, StarType

class Tussock(Genus):
    name: str = "Tussock"
    code = "TUS"
    colony_range = 200
    species: list[Species] = []

    def __init__(self):
        self.species.append(Albata())
        self.species.append(Capillum())
        self.species.append(Caputus())
        self.species.append(Catena())
        self.species.append(Cultro())
        self.species.append(Divisa())
        self.species.append(Ignis())
        self.species.append(Pennata())
        self.species.append(Pennatis())
        self.species.append(Propagito())
        self.species.append(Serrati())
        self.species.append(Stigmasis())
        self.species.append(Triticum())
        self.species.append(Ventusa())
        self.species.append(Virgam())
    
    def list_possible_species(self, star_system: Bodies, planet: dict[str, Any]) -> list[Species]:
        if PlanetType(planet["PlanetClass"]) == PlanetType.R:
            return super().list_possible_species(star_system, planet)
        else:
            return []

class Albata(Species):
    value: int = 3252500
    name: str = "Albata"
    code: str = "TUSALB"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (175, 180)

class Capillum(Species):
    value: int = 7025800
    name: str = "Capillum"
    code: str = "TUSCAP"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CH4, AtmosphereType.CH4_R, AtmosphereType.Ar, AtmosphereType.Ar_R]

class Caputus(Species):
    value: int = 3252500
    name: str = "Caputus"
    code: str = "TUSCPT"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (180, 190)

class Catena(Species):
    value: int = 1766600
    name: str = "Catena"
    code: str = "TUSCAT"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]

class Cultro(Species):
    value: int = 1766600
    name: str = "Cultro"
    code: str = "TUSCUL"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]

class Divisa(Species):
    value: int = 1766600
    name: str = "Divisa"
    code: str = "TUSDIV"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]

class Ignis(Species):
    value: int = 1849000
    name: str = "Ignis"
    code: str = "TUSIGN"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (160, 170)

class Pennata(Species):
    value: int = 5853800
    name: str = "Pennata"
    code: str = "TUSPEN"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (145, 155)

class Pennatis(Species):
    value: int = 1000000
    name: str = "Pennatis"
    code: str = "TUSPTS"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (-195, -195)

class Propagito(Species):
    value: int = 1000000
    name: str = "Propagito"
    code: str = "TUSPRO"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (-195, -195)

class Serrati(Species):
    value: int = 4447100
    name: str = "Serrati"
    code: str = "TUSSER"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (170, 175)

class Stigmasis(Species):
    value: int = 19010800
    name: str = "Stigmasis"
    code: str = "TUSSTI"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.SO2]

class Triticum(Species):
    value: int = 7774700
    name: str = "Triticum"
    code: str = "TUSTRI"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (190, 195)

class Ventusa(Species):
    value: int = 3277700
    name: str = "Ventusa"
    code: str = "TUSVEN"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (155, 160)

class Virgam(Species):
    value: int = 14313700
    name: str = "Virgam"
    code: str = "TUSVIR"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.H2O, AtmosphereType.H2O_R]