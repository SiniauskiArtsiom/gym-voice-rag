"""Neo4j client wrapper: connection, session, run_query."""
from contextlib import contextmanager
from typing import Iterator

from neo4j import GraphDatabase

from app.core.config import settings

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


def close_driver() -> None:
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


@contextmanager
def session() -> Iterator:
    driver = get_driver()
    with driver.session() as s:
        yield s


def run_query(cypher: str, params: dict | None = None) -> list[dict]:
    """Execute a Cypher query and return list of dicts."""
    with session() as s:
        result = s.run(cypher, params or {})
        return [record.data() for record in result]


def wipe_all() -> None:
    """Delete all nodes and relationships. Use with caution."""
    run_query("MATCH (n) DETACH DELETE n")


if __name__ == "__main__":
    rows = run_query("RETURN 1 AS n")
    print("Connection OK:", rows)
