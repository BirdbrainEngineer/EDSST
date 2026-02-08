from pathlib import Path
from enum import Enum, auto
import toml

EDSST_VERSION = "v0.1.2"

MODULE_VERSIONS_PATH = Path("module_versions.json")

config = toml.load("config.toml")

class TestingMode(Enum):
    Testing = auto()
    Release = auto()

TESTING_MODE: TestingMode = TestingMode.Testing if config.get("testing_mode", False) else TestingMode.Release