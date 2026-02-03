#from typing import Any
#from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType, PlanetType#, StarType

class Tubas(Genus):
    name: str = "Tubas"
    code = "TUB"
    colony_range = 800
    species: list[Species] = []
    
    def __init__(self):
        self.species.append(Cavas())
        self.species.append(Compagibus())
        self.species.append(Conifer())
        self.species.append(Rosarium())
        self.species.append(Sororibus())


class Cavas(Species):
    value: int = 11873200
    name: str = "Cavas"
    code: str = "TUBCAV"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (160, 190)
    planet_types: list[PlanetType] = [PlanetType.R]

class Compagibus(Species):
    value: int = 7774700
    name: str = "Compagibus"
    code: str = "TUBCOM"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (160, 190)
    planet_types: list[PlanetType] = [PlanetType.R]

class Conifer(Species):
    value: int = 2415500
    name: str = "Conifer"
    code: str = "TUBCON"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (160, 190)
    planet_types: list[PlanetType] = [PlanetType.R]

class Rosarium(Species):
    value: int = 2637500
    name: str = "Rosarium"
    code: str = "TUBROS"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]
    min_max_temperature: tuple[int, int] = (160, 160)
    planet_types: list[PlanetType] = [PlanetType.R]

class Sororibus(Species):
    value: int = 11873200
    name: str = "Sororibus"
    code: str = "TUBSOR"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R, AtmosphereType.NH3]
    min_max_temperature: tuple[int, int] = (160, 190)
    planet_types: list[PlanetType] = [PlanetType.HMC]