from html import escape
from src.version import MODULE_VERSIONS_PATH
import msgspec
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
import asyncio
import json
from pathlib import Path
from typing import Any

MODULES_DATA_PATH = Path("modules_data")

global_style = Style.from_dict({
    "edsst_color": "#ff8000",
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
    "error_bold": "#ff4040 bold",
    "warning_bold": "#ffff80 bold",
    "red_bold": "#ff0000 bold",
    "orange_bold": "#FF8000 bold",
    "yellow_bold": "#ffff00 bold",
    "lime_bold": "#80ff00 bold",
    "green_bold": "#00ff00 bold",
    "mint_bold": "#00ff80 bold",
    "cyan_bold": "#00ffff bold",
    "bright-blue_bold": "#0080ff bold",
    "blue_bold": "#0000ff bold",
    "violet_bold": "#8000ff bold",
    "magenta_bold": "#ff00ff bold",
    "deep-pink_bold": "#ff0080 bold",
    "white_bold": "#ffffff bold",
    "black_bold": "#000000 bold",
    "dark-grey_bold": "#404040 bold",
    "grey_bold": "#808080 bold",
    "light-grey_bold": "#b0b0b0 bold",
})

class ModuleState(msgspec.Struct):
    enabled: bool = False


class Module():
    style = Style.from_dict({
        "module_color": "#ffffff",
    })
    MODULE_NAME: str = "UNNAMED_MODULE"
    MODULE_VERSION: str = "?"
    STATE_TYPE = ModuleState
    module_dir: Path
    state_file_path: Path
    caught_up: bool = True
    state: ModuleState
    aliases: set[str]

    def __init__(self, extra_aliases: set[str]) -> None:
        self.aliases = set([f"{self.MODULE_NAME.lower()}"])
        for alias in extra_aliases: self.aliases.add(alias.lower())
        self.state = self.STATE_TYPE()
        module_versions: list[dict[str, str]] = []
        first_boot = True
        version_changed = False
        previous_version: str = "N/A"
        self.style = Style(self.style.style_rules + global_style.style_rules)
        self.module_dir = MODULES_DATA_PATH / Path(self.MODULE_NAME.lower())
        if not self.module_dir.exists():
            self.module_dir.mkdir()
        self.state_file_path = self.module_dir / Path(self.MODULE_NAME.lower() + "_state")
        if not MODULE_VERSIONS_PATH.exists():
            self.print("<error>Could not find versions file!</error> Attempting to make one.")
            module_versions.append({"module_name": self.MODULE_NAME, "version": self.MODULE_VERSION})
            first_boot = False
            try: 
                json.dump(module_versions, MODULE_VERSIONS_PATH.open("w"))
                self.print("<warning>New versions file successfully created!</warning>")
            except:
                self.print("<error>Could not create versions file!</error>")
        else:    
            try:
                module_versions = json.load(MODULE_VERSIONS_PATH.open())
            except:
                self.print("<error>Could not open versions file!</error>")
            for module in module_versions:
                if module["module_name"] == self.MODULE_NAME:
                    first_boot = False
                    previous_version = module["version"]
                    if previous_version != self.MODULE_VERSION:
                        module["version"] = self.MODULE_VERSION
                        version_changed = True
                        self.print("<warning>New module versions detected!</warning> ")
                        self.print(previous_version + " -> " + self.MODULE_VERSION)
                    try:    json.dump(module_versions, MODULE_VERSIONS_PATH.open("w"))
                    except: self.print("<error>Could not update versions file!</error>")
                    break
            if first_boot: module_versions.append({"module_name": self.MODULE_NAME, "version": self.MODULE_VERSION})
        if first_boot: self.print("<warning>First boot of module detected!</warning>")
        if version_changed:
            self.print("<warning>Initializing a new state file...</warning>")
            self.save_state()
        try:
            json.dump(module_versions, MODULE_VERSIONS_PATH.open("w"))
        except:
            self.print("<error>Could not update versions file!</error>")
        self.load_state()
        self.print(f"Loaded module version {self.MODULE_VERSION}")
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

    def save_state(self) -> None:
        if not self.caught_up: return
        self.state_file_path.write_bytes(msgspec.json.encode(self.state))

    def load_state(self) -> None:
        if self.state_file_path.exists():
            self.state = msgspec.json.decode(self.state_file_path.read_bytes(), type = self.STATE_TYPE)

    async def process_event(self, event: Any, tg: asyncio.TaskGroup) -> None:
        if event["event"] == "CaughtUp":
            self.caught_up = True

    async def process_user_input(self, arguments: list[str], tg: asyncio.TaskGroup) -> None:
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
