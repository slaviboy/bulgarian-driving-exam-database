"""master.sqlite must stay easy to consume from Android (Room / plain SQLite) — schema conventions."""

from __future__ import annotations

import re
import sqlite3

import pytest

from question_bank.database.sqlite_builder import schema_sql

ROOM_TYPES = {"TEXT", "INTEGER", "REAL", "BLOB"}


@pytest.fixture(scope="module")
def con():
    connection = sqlite3.connect(":memory:")
    connection.executescript(schema_sql())
    yield connection
    connection.close()


def tables(con) -> list[str]:
    rows = con.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")
    return sorted(r[0] for r in rows)


def test_no_extensions_or_without_rowid():
    sql = re.sub(r"--.*", "", schema_sql()).upper()  # ignore comments
    assert "WITHOUT ROWID" not in sql
    for feature in ("VIRTUAL TABLE", "FTS5", "FTS4", "RTREE", "JSON_", "GENERATED ALWAYS"):
        assert feature not in sql


def test_every_table_has_an_explicit_primary_key(con):
    for table in tables(con):
        pk = [row[1] for row in con.execute(f"PRAGMA table_info({table})") if row[5] > 0]
        assert pk, f"{table} has no explicit primary key"


def test_column_types_map_to_room_affinities(con):
    for table in tables(con):
        for _cid, name, declared, *_ in con.execute(f"PRAGMA table_info({table})"):
            assert declared.upper() in ROOM_TYPES, f"{table}.{name}: {declared}"


def test_foreign_keys_target_keys_and_are_indexed(con):
    for table in tables(con):
        for fk in con.execute(f"PRAGMA foreign_key_list({table})").fetchall():
            target, from_col, to_col = fk[2], fk[3], fk[4]
            target_pk = [row[1] for row in con.execute(f"PRAGMA table_info({target})") if row[5] > 0]
            assert to_col in target_pk, f"{table}.{from_col} → {target}.{to_col} is not a key"
            indexed_first_columns = set()
            for index in con.execute(f"PRAGMA index_list({table})").fetchall():
                columns = [c[2] for c in con.execute(f"PRAGMA index_info({index[1]})")]
                indexed_first_columns.add(columns[0])
            own_pk = [row[1] for row in con.execute(f"PRAGMA table_info({table})") if row[5] == 1]
            assert from_col in indexed_first_columns or from_col in own_pk, f"{table}.{from_col} not indexed"


def test_identifiers_are_snake_case(con):
    for table in tables(con):
        assert re.fullmatch(r"[a-z][a-z0-9_]*", table)
        for row in con.execute(f"PRAGMA table_info({table})"):
            assert re.fullmatch(r"[a-z][a-z0-9_]*", row[1]), f"{table}.{row[1]}"
