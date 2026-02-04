#from typing import Any
#from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType, PlanetType#, StarType

class Stratum(Genus):
    name: str = "Stratum"
    code = "STR"
    colony_range = 500
    species: list[Species] = []

    def __init__(self):
        self.species.append(Araneamus())
        self.species.append(Cucumisis())
        self.species.append(Excutitus())
        self.species.append(Frigus())
        self.species.append(Laminamus())
        self.species.append(Limaxus())
        self.species.append(Paleas())
        self.species.append(Tectonicas())


class Araneamus(Species):
    value: int = 2448900
    name: str = "Araneamus"
    code: str = "STRARA"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.SO2]
    min_max_temperature: tuple[int, int] = (165, 165)
    planet_types: list[PlanetType] = [PlanetType.R]

class Cucumisis(Species):
    value: int = 16202800
    name: str = "Cucumisis"
    code: str = "STRCUC"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.SO2, AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (190, 190)
    planet_types: list[PlanetType] = [PlanetType.R]

class Excutitus(Species):
    value: int = 2448900
    name: str = "Excutitus"
    code: str = "STREXC"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.SO2, AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (165, 190)
    planet_types: list[PlanetType] = [PlanetType.R]

class Frigus(Species):
    value: int = 2637500
    name: str = "Frigus"
    code: str = "STRFRI"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.SO2, AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (190, 190)
    planet_types: list[PlanetType] = [PlanetType.R]

class Laminamus(Species):
    value: int = 2788300
    name: str = "Laminamus"
    code: str = "STRLAM"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]
    min_max_temperature: tuple[int, int] = (165, 165)
    planet_types: list[PlanetType] = [PlanetType.R]

class Limaxus(Species):
    value: int = 1362000
    name: str = "Limaxus"
    code: str = "STRLIM"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.SO2, AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (165, 190)
    planet_types: list[PlanetType] = [PlanetType.R]

class Paleas(Species):
    value: int = 1362000
    name: str = "Paleas"
    code: str = "STRPAL"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R, AtmosphereType.NH3, AtmosphereType.H2O, AtmosphereType.H2O_R]
    min_max_temperature: tuple[int, int] = (165, 165)
    planet_types: list[PlanetType] = [PlanetType.R]

class Tectonicas(Species):
    value: int = 19010800
    name: str = "Tectonicas"
    code: str = "STRTEC"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.ANY]
    min_max_temperature: tuple[int, int] = (165, 165)
    planet_types: list[PlanetType] = [PlanetType.HMC]