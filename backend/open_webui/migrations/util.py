from __future__ import annotations

"""Alembic migration utilities."""

from alembic import op  # noqa: E402 — alembic runtime context
import sqlalchemy as sa
from sqlalchemy import inspect  # metadata inspection


def portable_string(length: int = 255) -> sa.types.TypeEngine:
    """Return a portable equivalent of an unbounded ``sa.String()`` column.

    Historical Open WebUI migrations frequently use ``sa.String()`` without a
    length. PostgreSQL and SQLite accept that declaration and retain their
    existing behavior, but SQLAlchemy refuses to compile it for MySQL/MariaDB
    because those dialects require an explicit length for ``VARCHAR``.

    ``TypeEngine.with_variant()`` keeps the original unbounded ``String`` type
    for PostgreSQL, SQLite, and any other dialect, while selecting
    ``VARCHAR(length)`` only when Alembic compiles or executes the migration for
    MySQL/MariaDB. This works in both online and ``alembic --sql`` modes and
    avoids global compiler monkey-patches that could silently change unrelated
    migration columns.

    Use this helper for ordinary string columns that were historically modeled
    with ``sa.String()``. For identifier-like text that participates in a
    primary key, unique constraint, index, or foreign key, use ``key_text()``
    instead.
    """
    return (
        sa.String()
        .with_variant(sa.String(length), 'mysql')
        .with_variant(sa.String(length), 'mariadb')
    )


def key_text(length: int = 255) -> sa.types.TypeEngine:
    """Return a dialect-aware type for text used in key or index paths.

    Open WebUI historically stores UUIDs and other identifiers in ``TEXT``
    columns. PostgreSQL and SQLite permit ``TEXT`` in primary keys, unique
    constraints, indexes, and foreign keys, so this helper deliberately keeps
    ``sa.Text()`` on those databases to preserve the existing schema and
    migration behavior.

    MySQL/MariaDB impose index-size and foreign-key type restrictions on
    ``TEXT``/``BLOB`` columns. In particular, an unbounded ``TEXT`` column
    cannot be used as a normal full-length key, and a foreign-key column must
    have a compatible type and length with the referenced column. Therefore,
    the MySQL and MariaDB variants use ``VARCHAR(length)``. The default length
    of 255 is sufficient for Open WebUI UUID-style identifiers; migrations with
    wide composite indexes can pass a smaller explicit length to stay within
    the InnoDB key-size limit.

    The variant is selected by SQLAlchemy at DDL compilation time, preserving
    PostgreSQL/SQLite behavior while making the MariaDB schema explicit in each
    revision. This is intentionally preferred over migration-environment
    compatibility shims, which can hide unsupported future migrations and rely
    on SQLAlchemy compiler internals.
    """
    return (
        sa.Text()
        .with_variant(sa.String(length), 'mysql')
        .with_variant(sa.String(length), 'mariadb')
    )


def get_primary_key_name_for_drop(
    conn: sa.engine.Connection,
    primary_key: dict[str, object],
) -> str | None:
    """Return the primary-key identifier Alembic should use when dropping it.

    PostgreSQL and SQLite normally preserve a named primary-key constraint, so
    their SQLAlchemy inspectors return the actual constraint name. MySQL and
    MariaDB are different: the server exposes the table primary key through
    the special identifier ``PRIMARY``, while SQLAlchemy inspection may report
    its ``name`` as ``None`` even when the migration originally supplied one.

    Alembic still requires a non-empty identifier for ``drop_constraint()``.
    Returning ``PRIMARY`` for an existing MySQL/MariaDB primary key allows the
    dialect compiler to emit the native ``ALTER TABLE ... DROP PRIMARY KEY``
    statement. Other dialects retain the inspector-provided name unchanged.

    ``None`` is returned when the table has no primary key or when an unnamed
    key cannot be normalized safely for the active database dialect.
    """
    name = primary_key.get('name')
    if name:
        return str(name)

    if primary_key.get('constrained_columns') and conn.dialect.name in {'mysql', 'mariadb'}:
        return 'PRIMARY'

    return None


# --- database helper functions ---
def get_existing_tables() -> set[str]:
    """Return table names already present in the database."""
    conn = op.get_bind()
    return set(inspect(conn).get_table_names())


def get_revision_id() -> str:
    """Generate a short random revision identifier."""
    import uuid

    return uuid.uuid4().hex[:12]
