from src.version import MODULE_VERSIONS_PATH
import msgspec
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
import asyncio
import json
from pathlib import Path
from typing import Any

global_style = Style.from_dict({
    "error": "#ff4040",
    "warning": "#ffff80",
    "red": "#ff0000",
    "orange": "#FF8000",
    "yellow": "#ffff00",
    "lime": "#80ff00",
    "green": "#00ff00",
    "mint": "#00ff80",
    "cyan": "#00ffff",
    "bright-blue": "#0080ff",
    "blue": "#0000ff",
    "violet": "#8000ff",
    "magenta": "#ff00ff",
    "deep-pink": "#ff0080",
    "white": "#ffffff",
    "black": "#000000",
    "dark-grey": "#404040",
    "grey": "#808080",
    "light-grey": "#b0b0b0",
})

class ModuleState(msgspec.Struct):
    enabled: bool = False


class Module():
    style = Style.from_dict({
        "module_color": "#ffffff",
    })

    MODULE_NAME: str = "UNNAMED_SURVEY"
    MODULE_VERSION: str = "?"
    STATE_TYPE = ModuleState
    module_dir: Path
    state_file_path: Path
    caught_up: bool = True
    state: ModuleState = ModuleState()

    def __init__(self) -> None:
        first_boot = False
        version_changed = False
        previous_version: str = "N/A"
        self.style = Style(self.style.style_rules + global_style.style_rules)
        self.print("Loading module version " + self.MODULE_VERSION + "...")
        self.module_dir = Path("modules") / Path(self.MODULE_NAME.lower())
        self.state_file_path = self.module_dir / Path(self.MODULE_NAME.lower() + "_state")
        if not self.module_dir.exists():
            self.module_dir.mkdir()
            first_boot = True

        try:
            module_versions = json.load(MODULE_VERSIONS_PATH.open())
            first_boot = True
            for module in module_versions:
                if module["module_name"] == self.MODULE_NAME:
                    first_boot = False
                    if module["version"] != self.MODULE_VERSION:
                        module["version"] = self.MODULE_VERSION
                        version_changed = True
                        json.dump(module_versions, MODULE_VERSIONS_PATH.open("w"))
                        break
            module_versions.append({"module_name": self.MODULE_NAME, "version": self.MODULE_VERSION})
            try:
                json.dump(module_versions, MODULE_VERSIONS_PATH.open("w"))
            except:
                self.print("<error>Could not add to versions file! EDSST is in a peculiar state... Tread with caution.</error>")
        except Exception as e: # pyright: ignore[reportUnusedVariable]
            if MODULE_VERSIONS_PATH.exists():
                self.print("Could not load version file!")
            else:
                self.print("<error>Could not find versions file!</error>")
                self.print("<warning>Attempting to make one.</warning>")
                module_versions: list[dict[str, Any]] = [{"module_name": self.MODULE_NAME, "version": self.MODULE_VERSION}]
                first_boot = True
                try:
                    json.dump(module_versions, MODULE_VERSIONS_PATH.open("w"))
                    self.print("<yellow>New versions file successfully created.</yellow>")
                except:
                    self.print("<error>Could not make a versions file! EDSST is in a peculiar state... Tread with caution.</error>")

        if first_boot: self.print("<warning>First boot of module detected!</warning>")
        if version_changed:
            self.print("<warning>New module version detected!</warning> ")
            self.print(previous_version + " -> " + self.MODULE_VERSION)

        try:
            self.load_state()
            self.save_state()
        except Exception as ex: # pyright: ignore[reportUnusedVariable]
            raise ex
            if not first_boot or not version_changed:
                self.print("<error>State file was found to be corrupted or missing! Data loss or corruption is possible!</error>")
            self.print("<warning>Initializing a new state file...</warning>")
            self.save_state()
        self.print("Module successfully loaded!")
        if self.state.enabled:
            self.print("Module currently <green>enabled</green>")
        else:
            self.print("Module currently <red>disabled</red>")

    def enable(self) -> None:
        if not self.state.enabled:
            self.state.enabled = True
            self.save_state()
        self.print("<green>Enabled!</green>")

    def disable(self) -> None:
        if self.state.enabled:
            self.state.enabled = False
            self.save_state()
        self.print("<red>Disabled!</red>")

    def save_state(self) -> None:   # Most likely this should 
        if not self.caught_up: return
        self.state_file_path.write_bytes(msgspec.json.encode(self.state))

    def load_state(self) -> None:
        if self.state_file_path.exists():
            self.state = msgspec.json.decode(self.state_file_path.read_bytes(), type = self.STATE_TYPE)

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:
        if event["event"] == "CaughtUp":
            self.caught_up = True

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
        if len(arguments) == 0:
            return
        elif arguments[0] == self.MODULE_NAME.lower():
            if len(arguments) < 2:
                self.print("<warning>Received no commands!</warning>")
                return
            match arguments[1]:
                case "enable":
                    self.enable()
                case "disable":
                    self.disable()
                case _: return

    def print(self, *values: str, sep: str = " ", end: str = "\n", prefix: str | None = None) -> None:
        if not self.caught_up: return
        html = sep.join(values)
        prefix = prefix if prefix != None else f"<module_color>{self.MODULE_NAME}</module_color>: "
        if prefix:
            html = prefix + html
        print_formatted_text(HTML(html), sep=sep, end=end, style=self.style)