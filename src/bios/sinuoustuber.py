from typing import Any
from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import PlanetType, AtmosphereType#, StarType

class SinuousTuber(Genus):
    name: str = "Sinuous Tuber"
    code = "SIN"
    colony_range = 100
    species: list[Species] = []

    def __init__(self):
        self.species.append(Albidum())
        self.species.append(Blatteum())
        self.species.append(Caeruleum())
        self.species.append(Lindigoticum())
        self.species.append(Prasinum())
        self.species.append(Roseus())
        self.species.append(Violaceum())
        self.species.append(Viride())

    def list_possible_species(self, star_system: Bodies, planet: dict[str, Any]) -> list[Species]:
        if AtmosphereType(planet["AtmosphereType"]) != AtmosphereType.NONE:
            return []
        else:
            if not planet["Volcanism"]:
                return []
            else:
                return super().list_possible_species(star_system, planet)

class Albidum(Species):
    value: int = 3425600
    name: str = "Albidum"
    code: str = "SINALB"
    planet_types: list[PlanetType] = [PlanetType.R]

class Blatteum(Species):
    value: int = 1514500
    name: str = "Blatteum"
    code: str = "SINBLA"
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC]

class Caeruleum(Species):
    value: int = 1514500
    name: str = "Caeruleum"
    code: str = "SINCAE"
    planet_types: list[PlanetType] = [PlanetType.R]

class Lindigoticum(Species):
    value: int = 1514500
    name: str = "Lindigoticum"
    code: str = "SINLIN"
    planet_types: list[PlanetType] = [PlanetType.R]

class Prasinum(Species):
    value: int = 1514500
    name: str = "Prasinum"
    code: str = "SINPRA"
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC]

class Roseus(Species):
    value: int = 1514500
    name: str = "Roseus"
    code: str = "SINROS"
    planet_types: list[PlanetType] = [PlanetType.R]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            if "silicate" in planet["Volcanism"].lower():
                return True
            else:
                return False
        else:
            return False

class Violaceum(Species):
    value: int = 1514500
    name: str = "Violaceum"
    code: str = "SINVIO"
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC]

class Viride(Species):
    value: int = 1514500
    name: str = "Viride"
    code: str = "SINVIR"
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC]
