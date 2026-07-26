"""Update folder table and change DateTime to BigInteger for timestamp fields

Revision ID: 4ace53fd72c8
Revises: af906e964978
Create Date: 2024-10-23 03:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = '4ace53fd72c8'
down_revision = 'af906e964978'
branch_labels = None
depends_on = None


def _is_mysql_family(conn) -> bool:
    """Return whether the active migration dialect is MySQL or MariaDB."""
    return conn.dialect.name in {'mysql', 'mariadb'}


def _upgrade_mysql_datetime_columns(conn) -> None:
    """Convert folder DATETIME columns to epoch seconds on MySQL/MariaDB.

    MariaDB does not support PostgreSQL's ``USING`` clause, and an implicit
    DATETIME-to-BIGINT cast does not produce Unix epoch seconds. Temporary
    columns make the conversion explicit and preserve the values before the
    original columns are removed. ``TIMESTAMPDIFF`` is used instead of
    ``UNIX_TIMESTAMP`` so a session time-zone setting cannot shift values that
    were historically stored as timezone-naive timestamps.
    """
    op.add_column('folder', sa.Column('created_at_epoch', sa.BigInteger(), nullable=True))
    op.add_column('folder', sa.Column('updated_at_epoch', sa.BigInteger(), nullable=True))

    folder = sa.table(
        'folder',
        sa.column('created_at', sa.DateTime()),
        sa.column('updated_at', sa.DateTime()),
        sa.column('created_at_epoch', sa.BigInteger()),
        sa.column('updated_at_epoch', sa.BigInteger()),
    )
    epoch = "'1970-01-01 00:00:00'"
    conn.execute(
        folder.update().values(
            created_at_epoch=sa.text(f'TIMESTAMPDIFF(SECOND, {epoch}, created_at)'),
            updated_at_epoch=sa.text(f'TIMESTAMPDIFF(SECOND, {epoch}, updated_at)'),
        )
    )

    op.drop_column('folder', 'created_at')
    op.drop_column('folder', 'updated_at')
    op.alter_column(
        'folder',
        'created_at_epoch',
        new_column_name='created_at',
        existing_type=sa.BigInteger(),
        existing_nullable=True,
        nullable=False,
    )
    op.alter_column(
        'folder',
        'updated_at_epoch',
        new_column_name='updated_at',
        existing_type=sa.BigInteger(),
        existing_nullable=True,
        nullable=False,
    )


def _downgrade_mysql_datetime_columns(conn) -> None:
    """Convert epoch seconds back to timezone-naive DATETIME values."""
    op.add_column('folder', sa.Column('created_at_datetime', sa.DateTime(), nullable=True))
    op.add_column('folder', sa.Column('updated_at_datetime', sa.DateTime(), nullable=True))

    folder = sa.table(
        'folder',
        sa.column('created_at', sa.BigInteger()),
        sa.column('updated_at', sa.BigInteger()),
        sa.column('created_at_datetime', sa.DateTime()),
        sa.column('updated_at_datetime', sa.DateTime()),
    )
    epoch = "'1970-01-01 00:00:00'"
    conn.execute(
        folder.update().values(
            created_at_datetime=sa.text(f'TIMESTAMPADD(SECOND, created_at, {epoch})'),
            updated_at_datetime=sa.text(f'TIMESTAMPADD(SECOND, updated_at, {epoch})'),
        )
    )

    op.drop_column('folder', 'created_at')
    op.drop_column('folder', 'updated_at')
    op.alter_column(
        'folder',
        'created_at_datetime',
        new_column_name='created_at',
        existing_type=sa.DateTime(),
        existing_nullable=True,
        nullable=False,
        server_default=sa.func.now(),
    )
    op.alter_column(
        'folder',
        'updated_at_datetime',
        new_column_name='updated_at',
        existing_type=sa.DateTime(),
        existing_nullable=True,
        nullable=False,
        server_default=sa.func.now(),
    )


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = {c['name']: c for c in inspector.get_columns('folder')}

    created_at_col = columns.get('created_at')
    if not created_at_col:
        return

    # Only convert if still DateTime — skip if already BigInteger
    if isinstance(created_at_col['type'], sa.BigInteger):
        return

    if _is_mysql_family(conn):
        _upgrade_mysql_datetime_columns(conn)
        return

    # Preserve the existing PostgreSQL and SQLite migration path. Alembic's
    # batch operation recreates the table when SQLite cannot alter the column
    # directly, while postgresql_using performs an explicit epoch conversion.
    with op.batch_alter_table('folder', schema=None) as batch_op:
        batch_op.alter_column('created_at', server_default=None)
        batch_op.alter_column('updated_at', server_default=None)
        batch_op.alter_column(
            'created_at',
            type_=sa.BigInteger(),
            existing_type=sa.DateTime(),
            existing_nullable=False,
            postgresql_using='extract(epoch from created_at)::bigint',
        )
        batch_op.alter_column(
            'updated_at',
            type_=sa.BigInteger(),
            existing_type=sa.DateTime(),
            existing_nullable=False,
            postgresql_using='extract(epoch from updated_at)::bigint',
        )


def downgrade():
    conn = op.get_bind()
    if _is_mysql_family(conn):
        _downgrade_mysql_datetime_columns(conn)
        return

    # Convert columns back to DateTime and restore defaults. Mirrors the
    # upgrade's postgresql_using cast — without it, Postgres can't
    # auto-cast BigInteger → timestamp and aborts with DatatypeMismatch.
    with op.batch_alter_table('folder', schema=None) as batch_op:
        batch_op.alter_column(
            'created_at',
            type_=sa.DateTime(),
            existing_type=sa.BigInteger(),
            existing_nullable=False,
            server_default=sa.func.now(),
            postgresql_using='to_timestamp(created_at)::timestamp without time zone',
        )
        batch_op.alter_column(
            'updated_at',
            type_=sa.DateTime(),
            existing_type=sa.BigInteger(),
            existing_nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            postgresql_using='to_timestamp(updated_at)::timestamp without time zone',
        )
