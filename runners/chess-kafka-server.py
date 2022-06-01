from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import asyncio
import json
import logging
import signal
import time
import typer
import ulid
import uvloop

from sqlmodel import Session, SQLModel
from typing import Optional

from database import engine

from actors.chess.app import App

from log import logging_init

app = typer.Typer()

logger = logging_init("cli")


@app.command()
def chess_server(app: str = typer.Option(...)):
    uvloop.install()
    asyncio.run(chess_server_async(app))


async def chess_server_async(app: str):
    logger.info(f"chess_server starting")

    # start app
    struct_app = App(
        toml_file=f"./data/apps/{app}.toml",
    ).call()

    # get app actors
    actors = [actor for name, actor in struct_app.actors.items()]

    def signal_handler(signum, frame):
        logger.info(f"chess_server signal handler ... cleaning up")
        for actor in actors:
            actor.cancel()

    # install signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # wait on tasks
    logger.info(f"chess_server wait on {len(actors)} actors")

    try:
        tasks = [actor.task for actor in actors]
        await asyncio.gather(*tasks)
    except:
        logger.error(f"chess_server exception {sys.exc_info()[0]}")


if __name__ == "__main__":
    app()
