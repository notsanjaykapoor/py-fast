import json
import logging
import re
import typing

from dataclasses import dataclass

import services.crypto.symmetric

from models.actor import Actor
from models.actor_log import ActorLog
from models.actor_message import ActorMessage

from services.crypto.symmetric.aesgcm.decrypt import AesGcmDecrypt


@dataclass
class Struct:
    code: int
    errors: list[str]


class WorkerSource:
    def __init__(self, app_name: str):
        self._app_name = app_name

        self._keys_file = "./keys/keys.toml"

        self._dict: dict = {}

        self._actor_log = ActorLog(app_name=self._app_name)
        self._logger = logging.getLogger("actor")

    # process kafka msg
    def call(self, actor: Actor, msg: ActorMessage) -> Struct:
        struct = Struct(0, [])

        self._logger.info(f"actor '{actor.name}' message header {msg.header()}")

        try:
            message_dict = json.loads(msg.value_str())

            self._logger.info(f"actor '{actor.name}' message {message_dict}")

            self._process(message_dict)

            # self._log_append(actor, msg)
        except Exception as e:
            struct.code = 500

            self._logger.error(f"actor '{actor.name}' exception {e}")

        return struct

    # append to app log
    def _log_append(self, actor: Actor, msg: ActorMessage):
        self._actor_log.append({"actor": actor.name, **msg.header()})

    def _process(self, actor: Actor, message_dict: dict):
        user_from = message_dict["from"]

        self._logger.info(f"actor '{actor.name}' from {user_from}")

        struct_factory = services.crypto.symmetric.Factory(
            self._keys_file, user_from
        ).call()

        cipher_name_ = services.crypto.symmetric.cipher_name(struct_factory.cipher)

        if cipher_name_ == "aesgcm":
            struct_decrypt = AesGcmDecrypt(
                cipher=struct_factory.cipher,
                encoded=message_dict["encoded"],
                nonce=message_dict["nonce"],
            ).call()
        else:
            raise ValueError("invalid cipher")

        return struct_decrypt.decoded
