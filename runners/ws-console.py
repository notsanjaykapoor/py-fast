from dotenv import load_dotenv

load_dotenv()  # read environment variables from .env

import asyncio
import json
import logging
import os
import sys
import typer
import ulid
import uvloop
import websockets

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from log import logging_init
from services.io.console_socket import IoConsoleSocket

logger = logging_init("console")

app = typer.Typer()


@app.command()
def ws_send(user_id: str = typer.Option(...)):
    uvloop.install()
    asyncio.run(ws_send_async(user_id))


async def ws_send_async(user_id: str):
    ws_url = f"{os.environ['WS_URL']}/ws/chat/{user_id}"

    logger.info(f"ws-console connecting {ws_url}")

    async with websockets.connect(ws_url) as ws:
        await IoConsoleSocket(user_id, ws).call()


if __name__ == "__main__":
    app()
