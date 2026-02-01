from pathlib import Path
from enum import Enum, auto

EDSST_VERSION = "v0.1.0"

MODULE_VERSIONS_PATH = Path("module_versions.json")

class TestingMode(Enum):
    Testing = auto()
    Release = auto()

TESTING_MODE: TestingMode = TestingMode.Release