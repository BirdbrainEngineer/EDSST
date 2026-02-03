from typing import Any
from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import StarType, PlanetType#, AtmosphereType

class Anemone(Genus):
    name: str = "Anemone"
    code: str = "ANE"
    colony_range = 100
    species: list[Species] = []

    def __init__(self):
        self.species.append(BlatteumBioluminescent())
        self.species.append(Croceum())
        self.species.append(Luteolum())
        self.species.append(PrasinumBioluminescent())
        self.species.append(Puniceum())
        self.species.append(Roseum())
        self.species.append(RoseumBioluminescent())
        self.species.append(RubeumBioluminescent())


    def list_possible_species(self, star_system: Bodies, planet: dict[str, Any]) -> list[Species]:
        if planet["Atmosphere"]:
            if planet["Atmosphere"] == "None":
                pass
            else:
                return []
        return super().list_possible_species(star_system, planet)
            


class BlatteumBioluminescent(Species):
    value: int = 1499900
    name: str = "Blatteum Bioluminescent"
    code: str = "ANEBLB"
    star_types: list[StarType] = [StarType("B", -1, "IV"), StarType("B", -1, "V")]
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC]

class Croceum(Species):
    value: int = 3399800
    name: str = "Croceum"
    code: str = "ANECRO"
    star_types: list[StarType] = [StarType("B", -1, "IV"), StarType("A", -1, "III")]
    planet_types: list[PlanetType] = [PlanetType.R]

class Luteolum(Species):
    value: int = 1499900
    name: str = "Luteolum"
    code: str = "ANELUT"
    star_types: list[StarType] = [StarType("B", -1, "IV"), StarType("B", -1, "V")]
    planet_types: list[PlanetType] = [PlanetType.R]

class PrasinumBioluminescent(Species):
    value: int = 1499900
    name: str = "Prasinum Bioluminescent"
    code: str = "ANEPRB"
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC, PlanetType.R]

class Puniceum(Species):
    value: int = 1499900
    name: str = "Puniceum"
    code: str = "ANEPUN"
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC, PlanetType.R, PlanetType.RI, PlanetType.I]

class Roseum(Species):
    value: int = 1499900
    name: str = "Roseum"
    code: str = "ANEROS"
    star_types: list[StarType] = [StarType("B", -1, "I"), StarType("B", -1, "II"), StarType("B", -1, "III")]
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC, PlanetType.R]

class RoseumBioluminescent(Species):
    value: int = 1499900
    name: str = "Roseum Bioluminescent"
    code: str = "ANEROB"
    star_types: list[StarType] = [StarType("B", -1, "I"), StarType("B", -1, "II"), StarType("B", -1, "III")]
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC, PlanetType.R]

class RubeumBioluminescent(Species):
    value: int = 1499900
    name: str = "Rubeum Bioluminescent"
    code: str = "ANERUB"
    star_types: list[StarType] = [StarType("B", -1, "I"), StarType("B", -1, "II"), StarType("B", -1, "III")]
    planet_types: list[PlanetType] = [PlanetType.MR, PlanetType.HMC]