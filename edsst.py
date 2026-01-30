### Elite: Dangerous Stellar Survey Tools

from src.modules.boxelsurvey import BoxelSurvey
from src.modules.fssreporter import FSSReporter
from src.modules.core import CoreModule
from src.modules.module import Module
from src.modules.dw3densitycolumnsurvey import DW3DensityColumnSurvey
from src.modules.examplemodule import ExampleModule
#from src.modules.edsm import EDSM
import src.version
from pathlib import Path
from typing import Iterator
import toml
from watchfiles import awatch # pyright: ignore[reportUnknownVariableType]
import json
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import traceback

# TODO: Spansh and/or EDSM integration.

config = toml.load("config.toml")

log_directory = Path(config["elite_dangerous_journal_path"])

def get_latest_journal_file_path() -> None | Path:
    log_paths: Iterator[Path] = log_directory.glob("Journal.*.log")

    latest_journal_file_path: Path | None = None
    for path in log_paths:
        if latest_journal_file_path is None:
            latest_journal_file_path = path
        latest_journal_file_path = max(latest_journal_file_path, path)
    
    return latest_journal_file_path

async def listen_for_events():
    initial_journal_file_path = get_latest_journal_file_path()

    if initial_journal_file_path:
        latest_journal_file_path = initial_journal_file_path
        with open(initial_journal_file_path) as file:
            file_by_lines = file.read().strip().split("\n")
            for line in file_by_lines:
                if not line: 
                    continue
                event = json.loads(line)
                yield event
    else:
        latest_journal_file_path = None

    if latest_journal_file_path:
        print("EDSST: Synchronized to journal file - " + str(latest_journal_file_path.name))
    else:
        print("EDSST: Did not find journal file.  Please confirm journal directory is set correctly in the config.toml file.")
        exit()

    yield {"event": "CaughtUp"}

    file = open(latest_journal_file_path)

    if latest_journal_file_path == initial_journal_file_path:
        file.read()
    ##start listening to the logfile
    async for changes in awatch(latest_journal_file_path, log_directory):
        for change, path in changes:
            del change
            if path == str(latest_journal_file_path):
                for line in file.read().strip().split("\n"):
                    if not line: 
                        continue
                    event = json.loads(line)
                    if event["event"] == "Shutdown":
                        print("EDSST: Detected shutdown.")
                    yield event
            else:
                new_latest_journal_file_path = get_latest_journal_file_path()
                if new_latest_journal_file_path and latest_journal_file_path != new_latest_journal_file_path:
                    print(f"EDSST: Synchronized to journal log file: {new_latest_journal_file_path}")
                    latest_journal_file_path = new_latest_journal_file_path
                    file.close()
                    file = open(latest_journal_file_path)

async def event_loop(modules: list[Module], tg: asyncio.TaskGroup):
    async for event in listen_for_events():
        for module in modules:
            if module.state.enabled or not module.caught_up:
                try:
                    await module.process_event(event, tg)
                except Exception:
                    module.state.enabled = False
                    print(traceback.format_exc())

async def input_loop(modules: list[Module], event_loop_task: asyncio.Task, tg: asyncio.TaskGroup) -> None: # pyright: ignore[reportUnknownParameterType, reportMissingTypeArgument]
    session = PromptSession() # pyright: ignore[reportUnknownVariableType]
    while True:
        with patch_stdout():
            result = await session.prompt_async(">>> ") # pyright: ignore[reportUnknownVariableType]
            if str(result).lower() == "exit": # pyright: ignore[reportUnknownArgumentType]
                event_loop_task.cancel()
                return
        arguments = str(result).lower().split() # pyright: ignore[reportUnknownArgumentType]
        if len(arguments) > 0:
            for module in modules:
                await module.process_user_input(arguments, tg) 

async def main():
    print("\nElite: Dangerous Stellar Survey Tools " + src.version.EDSST_VERSION + " booting...\n")

    #TODO: Make loading of modules dynamic

    modules: list[Module] = []
    core_module = CoreModule()
    modules.append(core_module)
    #modules.append(EDSM())
    modules.append(FSSReporter(core_module))
    modules.append(BoxelSurvey(core_module))
    modules.append(DW3DensityColumnSurvey(core_module))
    modules.append(ExampleModule())
    for module in modules:
        module.caught_up = False 
    

    async with asyncio.TaskGroup() as tg:
        event_loop_task = tg.create_task(event_loop(modules, tg))
        input_loop_task = tg.create_task(input_loop(modules, event_loop_task, tg)) # pyright: ignore[reportUnusedVariable]
        print("\n╔════════════════════════════════════════════════════════════╗\n" +
                "║ Elite: Dangerous Stellar Survey Tools successfully booted! ║\n" +
                "╚════════════════════════════════════════════════════════════╝\n")

asyncio.run(main())

exit("Elite: Dangerous Stellar Survey Tools spooling down...\nFarewell, Commander!")