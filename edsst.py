### Elite: Dangerous Stellar Survey Tools

from functools import partial
from src.modules.boxelsurvey import BoxelSurvey
from src.modules.fssreporter import FSSReporter
from src.modules.core import CoreModule
from src.modules.module import Module
from src.modules.dw3densitycolumnsurvey import DW3DensityColumnSurvey
from src.modules.chatboxrelay import ChatboxRelay
from src.modules.eddn.eddn import EDDN
from src.modules.edsm import EDSM
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
from src.version import TESTING_MODE, TestingMode
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit import print_formatted_text


config = toml.load("config.toml")

log_directory = Path(config["elite_dangerous_journal_path"])

edsst_style = Style.from_dict({
    "edsst_color": "#ff8000",
})

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
                event_raw = line
                event = json.loads(line)
                yield event, event_raw
    else:
        latest_journal_file_path = None

    if latest_journal_file_path:
        print_formatted_text(HTML("<edsst_color>EDSST</edsst_color>: Synchronized to journal file - " + str(latest_journal_file_path.name)), style=edsst_style)
    else:
        print_formatted_text(HTML("<edsst_color>EDSST</edsst_color>: Did not find journal file.  Please confirm journal directory is set correctly in the config.toml file."), style=edsst_style)
        exit()

    yield {"event": "CaughtUp"}, "{\"event\": \"CaughtUp\"}"

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
                    event_raw = line
                    event = json.loads(line)
                    if event["event"] == "Shutdown":
                        print_formatted_text(HTML("<edsst_color>EDSST</edsst_color>: Detected shutdown."), style=edsst_style)
                    yield event, event_raw
            else:
                new_latest_journal_file_path = get_latest_journal_file_path()
                if new_latest_journal_file_path and latest_journal_file_path != new_latest_journal_file_path:
                    print_formatted_text(HTML(f"<edsst_color>EDSST<edsst_color>: Synchronized to journal log file: {new_latest_journal_file_path.name}"), style=edsst_style)
                    latest_journal_file_path = new_latest_journal_file_path
                    file.close()
                    file = open(latest_journal_file_path)

async def event_loop(modules: list[Module], tg: asyncio.TaskGroup):
    async for event, event_raw in listen_for_events():
        for module in modules:
            if module.state.enabled or not module.caught_up:
                try:
                    await module.process_event(event, event_raw, tg)
                except Exception:
                    module.print(f"Encountered an unrecoverable error:")
                    print(traceback.format_exc())
                    module.disable()

async def process_user_input(modules: list[Module], tg: asyncio.TaskGroup, user_input: str):
    arguments = user_input.lower().split()
    if arguments:
        for module in modules:
            if arguments[0] in list(module.aliases):
                await module.process_user_input(arguments, tg) 


async def input_loop(modules: list[Module], event_loop_task: asyncio.Task, tg: asyncio.TaskGroup) -> None: # pyright: ignore[reportUnknownParameterType, reportMissingTypeArgument]
    session = PromptSession() # pyright: ignore[reportUnknownVariableType]
    while True:
        with patch_stdout():
            result = await session.prompt_async(">>> ") # pyright: ignore[reportUnknownVariableType]
            assert isinstance(result, str)
            if str(result).lower() == "exit":
                for module in modules:
                    module.save_state()
                event_loop_task.cancel()
                return
        await process_user_input(modules=modules, tg=tg, user_input=result)

async def main():
    print("\nElite: Dangerous Stellar Survey Tools " + src.version.EDSST_VERSION + " booting...\n")

    #TODO: Make loading of modules dynamic

    modules: list[Module] = []
    core_module = CoreModule()
    modules.append(core_module)
    modules.append(EDDN(core_module))
    modules.append(EDSM())
    modules.append(FSSReporter(core_module))
    modules.append(BoxelSurvey(core_module))
    modules.append(DW3DensityColumnSurvey(core_module))
    modules.append(ChatboxRelay(partial(process_user_input, modules)))
    #modules.append(ExampleModule())
    for module in modules:
        module.caught_up = False 
    

    async with asyncio.TaskGroup() as tg:
        event_loop_task = tg.create_task(event_loop(modules, tg))
        input_loop_task = tg.create_task(input_loop(modules, event_loop_task, tg)) # pyright: ignore[reportUnusedVariable]
        print("\n╔════════════════════════════════════════════════════════════╗\n" +
                "║ Elite: Dangerous Stellar Survey Tools successfully booted! ║\n" +
                "╚════════════════════════════════════════════════════════════╝\n")
        if TESTING_MODE == TestingMode.Testing:
            print_formatted_text(HTML("<edsst_color>      ╔════════════════════════════════════════════════╗</edsst_color>\n" +
                    "<edsst_color>      ║      !Booted in TESTING / DEBUGGING mode!      ║</edsst_color>\n" +
                    "<edsst_color>      ╚════════════════════════════════════════════════╝</edsst_color>\n"), style=edsst_style)

asyncio.run(main())

exit("Elite: Dangerous Stellar Survey Tools spooling down...\nFarewell, Commander!")