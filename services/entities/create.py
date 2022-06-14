import dataclasses
import logging
import sys

import sqlalchemy
import sqlmodel

import models


@dataclasses.dataclass
class Struct:
    code: int
    ids: list[str]
    count: int
    errors: list[str]


class Create:
    def __init__(self, db: sqlmodel.Session, entity_objects: list[dict]):
        self._db = db
        self._entity_objects = entity_objects

        self._logger = logging.getLogger("service")

    def call(self) -> Struct:
        struct = Struct(0, [], 0, [])

        self._logger.info(f"{__name__} {self._entity_objects}")

        try:
            for entity_object in self._entity_objects:
                db_object = models.Entity(
                    entity_id=entity_object["entity_id"],
                    entity_name=entity_object["entity_name"],
                    slug=entity_object["slug"],
                    type_name=entity_object["type_name"],
                    type_value=entity_object["type_value"],
                )
                self._db.add(db_object)
                self._db.commit()

                struct.ids.append(db_object.entity_id)
                struct.count += 1
        except sqlalchemy.exc.IntegrityError:
            self._db.rollback()
            struct.code = 409
            self._logger.error(f"{__name__} {sys.exc_info()[0]} error")
        except Exception:
            self._db.rollback()
            struct.code = 500
            self._logger.error(f"{__name__} {sys.exc_info()[0]} exception")

        return struct
