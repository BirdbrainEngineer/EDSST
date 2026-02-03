#from typing import Any
#from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType, PlanetType#, StarType

class Frutexa(Genus):
    name: str = "Frutexa"
    code = "FRU"
    colony_range = 150
    species: list[Species] = []

    def __init__(self):
        self.species.append(Acus())
        self.species.append(Collum())
        self.species.append(Fera())
        self.species.append(Flabellum())
        self.species.append(Flammasis())
        self.species.append(Metallicum())
        self.species.append(Sponsae())

class Acus(Species):
    value: int = 7774700
    name: str = "Acus"
    code: str = "FRUACU"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (-195, -195)
    planet_types: list[PlanetType] = [PlanetType.R]

class Collum(Species):
    value: int = 1639800
    name: str = "Collum"
    code: str = "FRUCOL"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.SO2]
    planet_types: list[PlanetType] = [PlanetType.R]

class Fera(Species):
    value: int = 1632500
    name: str = "Fera"
    code: str = "FRUFER"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (-195, -195)
    planet_types: list[PlanetType] = [PlanetType.R]

class Flabellum(Species):
    value: int = 1808900
    name: str = "Flabellum"
    code: str = "FRUFLA"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]
    planet_types: list[PlanetType] = [PlanetType.R]

class Flammasis(Species):
    value: int = 10326000
    name: str = "Flammasis"
    code: str = "FRUFLA"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]
    planet_types: list[PlanetType] = [PlanetType.R]

class Metallicum(Species):
    value: int = 1632500
    name: str = "Metallicum"
    code: str = "FRUMET"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R, AtmosphereType.NH3]
    planet_types: list[PlanetType] = [PlanetType.HMC]

class Sponsae(Species):
    value: int = 5988000
    name: str = "Sponsae"
    code: str = "FRUSPO"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.H2O, AtmosphereType.H2O_R]
    planet_types: list[PlanetType] = [PlanetType.R]
