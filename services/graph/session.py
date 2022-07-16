import os

import neo4j


def get() -> neo4j.Session:
    return _get_driver().session(database=os.environ["NEO4J_DB_NAME"])


def _get_driver() -> neo4j.Driver:
    driver = neo4j.GraphDatabase.driver(
        os.environ["NEO4J_HOST_URL"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
    )

    return driver
