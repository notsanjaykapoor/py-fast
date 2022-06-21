#!/usr/bin/env python

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402
import sys  # noqa: E402

import datadog  # noqa: E402
import typer  # noqa: E402

sys.path.insert(1, os.path.join(sys.path[0], ".."))

import log  # noqa: E402
import services.database.session  # noqa: E402
import services.entities  # noqa: E402
import services.graph.distance  # noqa: E402
import services.graph.query  # noqa: E402
import services.graph.session  # noqa: E402
import services.graph.tx  # noqa: E402

logger = log.logging_init("cli")

app = typer.Typer()


@app.command()
def geo(
    node: str = typer.Option(...),
    radius: str = typer.Option(None, "--radius", "-r"),
):
    """find neighbors filtered by distance"""

    name, id = node.split(":", 1)

    meters = services.graph.distance.meters(radius)

    struct_graph = services.graph.query.match_geo_distance_from_node(
        src_label=name,
        src_id=id,
        meters=meters,
    )

    # struct_graph = services.graph.query.match_geo_distance_from_point(
    #     lat=41.8911752,
    #     lon=-87.6321491,
    #     dst_label="place",
    #     dst_id="01G5YPTKXDWA1DC19W2963SJZW",
    #     meters=meters,
    # )

    logger.info(f"[graph-cli] query '{struct_graph.query}' params {struct_graph.params}")

    with datadog.statsd.timed(f"{__name__}.timer", tags=["env:dev", "neo:read"]):
        with services.graph.session.get() as neo:
            records = neo.read_transaction(services.graph.tx.read, struct_graph.query, struct_graph.params)

    if not records:
        logger.info("[graph-cli] no records found")

    for i, record in enumerate(records):
        logger.info("")

        logger.info(f"[graph-cli] record {i+1} {record}")


@app.command()
def neighbors(
    node: str = typer.Option(...),
    max_hops: int = typer.Option(1),
):
    """find all neighbors filtered by label and constrained by hops"""

    name, id = node.split(":", 1)

    with services.database.session.get() as db:
        struct_list = services.entities.ListEntityNames(db).call()
        # map to list of list values, e.g. [['case'], ['person']]
        node_labels = [[s] for s in struct_list.values]

    query = f"match p = (a:{name} {{id: $id_1}})-[*1.." + str(max_hops) + "]-(b) " f"where labels(b) in {node_labels} " + "return distinct(b) as n"

    # query = (
    #     f"match p = (s:{name} {{id: $id_1}})-[*1.."
    #     + str(max_hops)
    #     + f"]-(e) return s,e,relationships(p) as r"
    # )

    # query = f"match (a:{name} {{id: $id_1}})-[*1..10]-(b) where labels(b) in [['case'], ['person']] return distinct(b) as n"

    params = {
        "id_1": id,
    }

    logger.info(f"[graph-cli] {query} {params}")

    with services.graph.session.get() as neo:
        records = neo.read_transaction(services.graph.tx.read, query, params)

    if not records:
        logger.info("[graph-cli] no records found")

    for i, record in enumerate(records):
        logger.info("")

        node = record["n"]

        logger.info(f"[graph-cli] record {i+1}")
        logger.info(f"[graph-cli] node {node}")

        # node_start = record["s"]
        # node_end = record["e"]
        # relationships = record["r"]

        # logger.info(f"[graph-cli] start {node_start}")
        # logger.info(f"[graph-cli] end {node_end}")
        # logger.info(f"[graph-cli] rels {relationships}")


@app.command()
def shortest_path(
    node_1: str = typer.Option(...),
    node_2: str = typer.Option(...),
):
    """find all shortest path between nodes"""

    name_1, id_1 = node_1.split(":", 1)
    name_2, id_2 = node_2.split(":", 1)

    query = f"""
    match (p1:{name_1} {{id: $id_1}}), (p2:{name_2} {{id: $id_2}}), p = allShortestPaths((p1)-[r*]-(p2)) return p
    """

    params = {
        "id_1": id_1,
        "id_2": id_2,
    }

    logger.info(f"[graph-cli] {query} {params}")

    with services.graph.session.get() as neo:
        records = neo.read_transaction(services.graph.tx.read, query, params)

    if not records:
        logger.info("[graph-cli] no path found")

    for i, record in enumerate(records):
        logger.info("")

        path = record["p"]

        logger.info(f"[graph-cli] path {i+1}")

        for node in path.nodes:
            logger.info(f"[graph-cli] node {node.labels} {node.items()}")


if __name__ == "__main__":
    app()
