from typing import Any
from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType, PlanetType#, StarType 

class Concha(Genus):
    name: str = "Concha"
    code = "CON"
    colony_range = 150
    species: list[Species] = []

    def __init__(self):
        self.species.append(Aureolas())
        self.species.append(Biconcavis())
        self.species.append(Labiata())
        self.species.append(Renibus())
    
    def list_possible_species(self, star_system: Bodies, planet: dict[str, Any]) -> list[Species]:
        if self.check_if_gravity_less_than(planet, 0.27):
            return super().list_possible_species(star_system, planet)
        else:
            return []
        

class Aureolas(Species):
    value: int = 7774700
    name: str = "Aureolas"
    code: str = "CONAUR"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

class Biconcavis(Species):
    value: int = 16777215
    name: str = "Biconcavis"
    code: str = "CONBIC"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.N2]

class Labiata(Species):
    value: int = 2352400
    name: str = "Labiata"
    code: str = "CONLAB"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]
    min_max_temperature: tuple[int, int] = (-190, -190)
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

class Renibus(Species):
    value: int = 4572400
    name: str = "Renibus"
    code: str = "CONREN"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R, AtmosphereType.H2O, AtmosphereType.H2O_R]
    min_max_temperature: tuple[int, int] = (180, 195)
    planet_types: list[PlanetType] = [PlanetType.R, PlanetType.HMC]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if AtmosphereType(planet["AtmosphereType"]) in (AtmosphereType.H2O, AtmosphereType.H2O_R):
            return True
        else:
            return super().check_viability(star_system, planet)