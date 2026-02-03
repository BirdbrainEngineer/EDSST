from typing import Any
from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType#, StarType, PlanetType

class Bacterium(Genus):
    name: str = "Bacterium"
    code: str = "BAC"
    colony_range = 500
    species: list[Species] = []

    def __init__(self):
        self.species.append(Acies())
        self.species.append(Alcyoneum())
        self.species.append(Aurasus())
        self.species.append(Bullaris())
        self.species.append(Cerbrus())
        self.species.append(Informem())
        self.species.append(Nebulus())
        self.species.append(Omentum())
        self.species.append(Scopulum())
        self.species.append(Tela())
        self.species.append(Verrata())
        self.species.append(Vesicula())
        self.species.append(Volu())

class Acies(Species):
    value: int = 1000000
    name: str = "Acies"
    code: str = "BACACI"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.Ne, AtmosphereType.Ne_R]

class Alcyoneum(Species):
    value: int = 1658500 
    name: str = "Alcyoneum"
    code: str = "BACALC"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NH3]

class Aurasus(Species):
    value: int = 1000000
    name: str = "Aurasus"
    code: str = "BACAUR"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CO2, AtmosphereType.CO2_R]

class Bullaris(Species):
    value: int = 1152500
    name: str = "Bullaris"
    code: str = "BACBUL"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.CH4, AtmosphereType.CH4_R]

class Cerbrus(Species):
    value: int = 1689800
    name: str = "Cerbrus"
    code: str = "BACCER"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.H2O, AtmosphereType.SO2]

class Informem(Species):
    value: int = 8418000
    name: str = "Informem"
    code: str = "BACINF"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.N2]

class Nebulus(Species):
    value: int = 9116600
    name: str = "Nebulus"
    code: str = "BACNEB"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.He]

class Omentum(Species):
    value: int = 4638900
    name: str = "Omentum"
    code: str = "BACOME"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.Ne, AtmosphereType.Ne_R]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            if "nitrogen" in planet["Volcanism"].lower() or "ammonia" in planet["Volcanism"].lower():
                return True
            else:
                return False
        else:
            return False

class Scopulum(Species):
    value: int = 8633800
    name: str = "Scopulum"
    code: str = "BACSCO"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.Ne, AtmosphereType.Ne_R]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            if "carbon" in planet["Volcanism"].lower() or "methane" in planet["Volcanism"].lower():
                return True
            else:
                return False
        else:
            return False

class Tela(Species):
    value: int = 1949000
    name: str = "Tela"
    code: str = "BACTEL"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.ANY]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            if planet["Volcanism"]:
                return True
            elif "helium" in planet["Volcanism"].lower() or "iron" in planet["Volcanism"].lower() or "silicate" in planet["Volcanism"].lower():
                return True
            else:
                return False
        else:
            return False

class Verrata(Species):
    value: int = 3897000
    name: str = "Verrata"
    code: str = "BACVER"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.Ne, AtmosphereType.Ne_R]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            if "water" in planet["Volcanism"].lower():
                return True
            else:
                return False
        else:
            return False

class Vesicula(Species):
    value: int = 1000000
    name: str = "Vesicula"
    code: str = "BACVES"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.Ar, AtmosphereType.Ar_R]
 
class Volu(Species):
    value: int = 7774700
    name: str = "Volu"
    code: str = "BACVOL"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.O2]







 

 

