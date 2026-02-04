from typing import Any
from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType, PlanetType#, StarType



class Aleoida(Genus):
    name: str = "Aleoida"
    code: str = "ALE"
    colony_range: int = 150
    species: list[Species] = []  

    def __init__(self):
        self.species.append(Arcus())
        self.species.append(Coronamus())
        self.species.append(Gravis())
        self.species.append(Laminae())
        self.species.append(Spica())

    def list_possible_species(self, star_system: Bodies, planet: dict[str, Any]) -> list[Species]:
        if self.check_if_gravity_less_than(planet, 0.27):
            return super().list_possible_species(star_system, planet)
        else:
            return []


class Arcus(Species):
    value: int = 7252500
    name: str = "Arcus"
    code: str = "ALEARC"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (175, 180)
    planet_types: list[PlanetType] = [PlanetType.HMC, PlanetType.R]

class Coronamus(Species):
    value: int = 6284600
    name: str = "Coronamus"
    code: str = "ALECOR"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (180, 190)
    planet_types: list[PlanetType] = [PlanetType.HMC, PlanetType.R]

class Gravis(Species):
    value: int = 12934900 
    name: str = "Gravis"
    code: str = "ALEGRA"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (190, 195)
    planet_types: list[PlanetType] = [PlanetType.HMC, PlanetType.R]

class Laminae(Species):
    value: int = 3385200 
    name: str = "Laminae"
    code: str = "ALELAM"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]
    planet_types: list[PlanetType] = [PlanetType.HMC, PlanetType.R]

class Spica(Species):
    value: int = 3385200 
    name: str = "Spica"
    code: str = "ALESPI"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]
    planet_types: list[PlanetType] = [PlanetType.HMC, PlanetType.R]