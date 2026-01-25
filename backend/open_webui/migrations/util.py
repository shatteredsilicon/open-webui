import sqlalchemy as sa
from alembic import op
from sqlalchemy import Inspector


def _dialect_name(conn=None) -> str:
    """
    Return current dialect name.
    Uses Alembic bind by default (safe inside migrations).
    """
    if conn is None:
        conn = op.get_bind()
    return (conn.dialect.name or "").lower()


def key_text(conn=None, length: int = 255):
    """
    Dialect-aware TEXT for identifiers/keys.
    - MySQL/MariaDB: TEXT cannot be indexed/PK'd without prefix length => use VARCHAR(length).
    - PostgreSQL/SQLite: keep TEXT (historical behavior).
    """
    d = _dialect_name(conn)
    if d in ("mysql", "mariadb"):
        return sa.String(length=length)
    return sa.Text()


def get_existing_tables():
    con = op.get_bind()
    inspector = Inspector.from_engine(con)
    tables = set(inspector.get_table_names())
    return tables


def get_revision_id():
    import uuid

    return str(uuid.uuid4()).replace("-", "")[:12]
