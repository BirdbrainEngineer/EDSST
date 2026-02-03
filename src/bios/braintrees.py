from typing import Any
from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import PlanetType, AtmosphereType#, StarType

class BrainTrees(Genus):
    name: str = "BrainTree"
    code: str = "BRA"
    colony_range = 100
    species: list[Species] = []

    def __init__(self):
        self.species.append(Aureum())
        self.species.append(Gypseeum())
        self.species.append(Lindigoticum())
        self.species.append(Lividum())
        self.species.append(Ostrinum())
        self.species.append(Puniceum())
        self.species.append(Roseum())
        self.species.append(Viride())

    def list_possible_species(self, star_system: Bodies, planet: dict[str, Any]) -> list[Species]:
        if AtmosphereType(planet["AtmosphereType"]) != AtmosphereType.NONE:
            return []
        else:
            if not planet["Volcanism"]:
                return []
            else:
                return super().list_possible_species(star_system, planet)


class Aureum(Species):
    value: int = 3565100
    name: str = "Aureum"
    code: str = "BRAAUR"
    min_max_temperature: tuple[int, int] = (300, 500)
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC]

class Gypseeum(Species):
    value: int = 3565100
    name: str = "Gypseeum"
    code: str = "BRAGYP"
    min_max_temperature: tuple[int, int] = (200, 300)
    planet_types: list[PlanetType] = [PlanetType.R]

class Lindigoticum(Species):
    value: int = 3565100
    name: str = "Lindigoticum"
    code: str = "BRALIN"
    min_max_temperature: tuple[int, int] = (300, 500)
    planet_types: list[PlanetType] = [PlanetType.HMC, PlanetType.R]

class Lividum(Species):
    value: int = 1593700
    name: str = "Lividum"
    code: str = "BRALIV"
    min_max_temperature: tuple[int, int] = (300, 500)
    planet_types: list[PlanetType] = [PlanetType.R]

class Ostrinum(Species):
    value: int = 3565100
    name: str = "Ostrinum"
    code: str = "BRAOST"
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC]

class Puniceum(Species):
    value: int = 3565100
    name: str = "Puniceum"
    code: str = "BRAPUN"
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC]

class Roseum(Species):
    value: int = 1593700
    name: str = "Roseum"
    code: str = "BRAROS"
    min_max_temperature: tuple[int, int] = (200, 500)

class Viride(Species):
    value: int = 1593700
    name: str = "Viride"
    code: str = "BRAVIR"
    min_max_temperature: tuple[int, int] = (100, 270)
    planet_types: list[PlanetType] = [PlanetType.RI]