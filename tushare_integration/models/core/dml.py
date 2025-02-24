from typing import Any, Optional, Self, Sequence, Type, Union, cast

from sqlalchemy import Table, inspect
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.dml import Insert


class Replace(Insert):
    """Represents a REPLACE INTO statement with chainable interface."""

    inherit_cache = False

    def __init__(self, *arg: Any, **kw: Any):
        super().__init__(*arg, **kw)
        self._on: Optional[Union[str, Sequence[str], ClauseElement]] = None

    def on(self, on_clause: Union[str, Sequence[str], ClauseElement]) -> Self:
        """Specify ON clause for the REPLACE statement."""
        self._on = on_clause
        return self


@compiles(Replace, 'databend')
def compile_upsert_databend(insert: Replace, compiler: Any, **kw: Any) -> str:
    # First generate the INSERT statement
    insert_stmt = compiler.visit_insert(insert, **kw)

    # Replace 'INSERT INTO' with 'REPLACE INTO'
    replace_stmt = insert_stmt.replace('INSERT INTO', 'REPLACE INTO', 1)

    # Add ON clause before VALUES if specified
    if insert._on is not None:
        if isinstance(insert._on, (str, ClauseElement)):
            on_clause = f" ON ({insert._on})"
        elif isinstance(insert._on, Sequence):
            on_clause = f" ON ({', '.join(insert._on)})"
        elif isinstance(insert._on, list):
            on_clause = f" ON ({', '.join(insert._on)})"
        else:
            raise ValueError(f"Invalid ON clause type: {type(insert._on)}")
        # Insert the ON clause before VALUES
        values_pos = replace_stmt.find('VALUES')
        if values_pos != -1:
            replace_stmt = replace_stmt[:values_pos] + on_clause + ' ' + replace_stmt[values_pos:]

    return replace_stmt


@compiles(Replace, 'mysql')
def compile_upsert_mysql(insert: Replace, compiler: Any, **kw: Any) -> str:
    # First generate the INSERT statement
    insert_stmt = compiler.visit_insert(insert, **kw)

    # Replace 'INSERT INTO' with 'REPLACE INTO'
    replace_stmt = insert_stmt.replace('INSERT INTO', 'REPLACE INTO', 1)

    return replace_stmt


@compiles(Replace, 'duckdb')
def compile_upsert_duckdb(insert: Replace, compiler: Any, **kw: Any) -> str:
    # First generate the INSERT statement
    insert_stmt = compiler.visit_insert(insert, **kw)

    replace_stmt = insert_stmt.replace('INSERT INTO', 'INSERT OR REPLACE INTO', 1)

    return replace_stmt


def upsert(table: Union[Table, Type['DeclarativeBase']]) -> Replace:
    """Create a Replace DML instance for the table."""
    pks = []
    if (inspected_schema := inspect(table)) is not None:
        pks = [col.name for col in inspected_schema.primary_key]

    if not pks:
        raise ValueError(f"Table {table} does not have a primary key defined.")

    if hasattr(table, '__table__'):
        table = cast(Table, getattr(table, '__table__'))
    return Replace(table).on(pks)
