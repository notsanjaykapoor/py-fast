import dataclasses
import logging
import typing

import sqlmodel

import models


@dataclasses.dataclass
class Struct:
    code: int
    ids: typing.List[str]
    ids_count: int
    errors: typing.List[str]


class ListIds:
    def __init__(self, db: sqlmodel.Session):
        self._db = db

        self._dataset = sqlmodel.select(models.Entity.entity_id).distinct()
        self._logger = logging.getLogger("api")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        struct.ids = self._db.exec(self._dataset).all()
        struct.ids_count = len(struct.ids)

        return struct
