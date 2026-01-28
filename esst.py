### Elite: Dangerous Stellar Survey Tools

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

from src.program import CoreProgram, BoxelSurvey, DW3DensityColumnSurvey, Program, FSSReporter

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
                if event["event"] == "Shutdown":
                    latest_journal_file_path = None
                yield event
    else:
        latest_journal_file_path = None

    if latest_journal_file_path:
        print("EDSST: Synchronized to journal file - " + str(latest_journal_file_path.name))

    yield {"event": "CaughtUp"}

    while True:
        if latest_journal_file_path:
            with open(latest_journal_file_path) as file:
                if latest_journal_file_path == initial_journal_file_path:
                    file.read()
                ##start listening to the logfile
                async for changes in awatch(latest_journal_file_path, log_directory):
                    for change, path in changes:
                        del change
                        if path == str(log_directory):
                            new_latest_journal_file_path = get_latest_journal_file_path()
                            if not new_latest_journal_file_path or latest_journal_file_path == new_latest_journal_file_path:
                                continue
                            else:
                                latest_journal_file_path = new_latest_journal_file_path
                                print("EDSST: Found a new journal log file!")
                        elif path == str(latest_journal_file_path):
                            for line in file.read().strip().split("\n"):
                                if not line: 
                                    continue
                                event = json.loads(line)
                                if event["event"] == "Shutdown":
                                    break
                                yield event
        print("EDSST: Elite: Dangerous not running. Waiting for new journal log file.")

async def event_loop(modules: list[Program], tg: asyncio.TaskGroup):
    async for event in listen_for_events():
        for module in modules:
            if module.state.enabled or not module.caught_up:
                try:
                    await module.process_event(event, tg)
                except Exception:
                    module.state.enabled = False
                    print(traceback.format_exc())

async def input_loop(modules: list[Program], event_loop_task: asyncio.Task, tg: asyncio.TaskGroup) -> None: # pyright: ignore[reportUnknownParameterType, reportMissingTypeArgument]
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

    print("\nElite: Dangerous Stellar Survey Tools " + src.version.ESST_VERSION + " booting...\n")

    #TODO: Make loading of modules dynamic

    modules: list[Program] = []
    core_module = CoreProgram()
    modules.append(core_module)
    modules.append(FSSReporter(core_module))
    modules.append(BoxelSurvey(core_module))
    modules.append(DW3DensityColumnSurvey(core_module))
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