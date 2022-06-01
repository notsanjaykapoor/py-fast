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
import websocket

from database import engine
from sqlmodel import Session, SQLModel
from typing import Optional

from kafka.reader import KafkaReader
from kafka.writer import KafkaWriter

from log import logging_init

from services.crypto.symmetric.aesgcm.encrypt import AesGcmEncrypt
from services.crypto.symmetric.factory import SymmetricFactory
from services.crypto.symmetric.name import cipher_name

app = typer.Typer()

logger = logging_init("cli")


@app.command()
def crypto_client(
    topic: str = typer.Option(...),
    user_id: str = "kafka@notme.com",
    keys_file: str = "./keys/keys.toml",
):
    writer = KafkaWriter(topic=topic)

    logger.info(f"crypto_client topic {topic} user_id {user_id}")

    struct_factory = SymmetricFactory(keys_file, user_id).call()

    message = {
        "message": "ping",
        "id": ulid.new().str,
    }

    cipher_name_ = cipher_name(struct_factory.cipher)

    if cipher_name_ == "aesgcm":
        struct_encrypt = AesGcmEncrypt(
            cipher=struct_factory.cipher,
            data=message,
        ).call()
    else:
        raise ValueError("invalid cipher")

    # logger.info(f"crypto_client struct {struct_encrypt}")

    writer = KafkaWriter(topic=topic)

    writer.call(
        key=ulid.new().str,
        message={
            "from": user_id,
            "encoded": struct_encrypt.encoded,
            "nonce": struct_encrypt.nonce,
        },
    )


if __name__ == "__main__":
    app()
