#from typing import Any
#from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType, PlanetType#, StarType

class Cactoida(Genus):
    name: str = "Cactoida"
    code: str = "CAC"
    colony_range = 300
    species: list[Species] = []

    def __init__(self):
        self.species.append(Cortexum())
        self.species.append(Lapis())
        self.species.append(Peperatis())
        self.species.append(Pullulanta())
        self.species.append(Vermis())


class Cortexum(Species):
    value: int = 3667600
    name: str = "Cortexum"
    code: str = "CACCOR"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

class Lapis(Species):
    value: int = 2483600
    name: str = "Lapis"
    code: str = "CACLAP"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

class Peperatis(Species):
    value: int = 2483600
    name: str = "Peperatis"
    code: str = "CACPEP"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

class Pullulanta(Species):
    value: int = 3667600
    name: str = "Pullulanta"
    code: str = "CACPUL"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (180, 195)
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

class Vermis(Species):
    value: int = 16202800
    name: str = "Vermis"
    code: str = "CACVER"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.H2O, AtmosphereType.H2O_R]
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

    
