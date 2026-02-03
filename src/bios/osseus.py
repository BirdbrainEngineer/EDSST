#from typing import Any
#from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType, PlanetType#, StarType

class Osseus(Genus):
    name: str = "Osseus"
    code = "OSS"
    colony_range = 800
    species: list[Species] = []

    def __init__(self):
        self.species.append(Cornibus())
        self.species.append(Discus())
        self.species.append(Fractus())
        self.species.append(Pellebantus())
        self.species.append(Pumice())
        self.species.append(Spiralis())


class Cornibus(Species):
    value: int = 1483000
    name: str = "Cornibus"
    code: str = "OSSCOR"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (180, 195)
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

class Discus(Species):
    value: int = 12934900
    name: str = "Discus"
    code: str = "OSSDIS"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.H2O, AtmosphereType.H2O_R]
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

class Fractus(Species):
    value: int = 4027800
    name: str = "Fractus"
    code: str = "OSSFRA"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (180, 190)
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

class Pellebantus(Species):
    value: int = 9739000
    name: str = "Pellebantus"
    code: str = "OSSPEL"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (190, 195)
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

class Pumice(Species):
    value: int = 3156300
    name: str = "Pumice"
    code: str = "OSSPUM"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CH4, AtmosphereType.CH4_R, AtmosphereType.Ar, AtmosphereType.Ar_R, AtmosphereType.N2]
    planet_types: list[PlanetType] = [PlanetType.RI]

class Spiralis(Species):
    value: int = 2404700
    name: str = "Spiralis"
    code: str = "OSSSPI"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]