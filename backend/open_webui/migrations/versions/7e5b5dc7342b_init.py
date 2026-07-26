# Initial bootstrap migration version.
# Revision ID: 7e5b5dc7342b
# Revises: (none)
# Created on: 2024-06-24 13:15:33.808998
from __future__ import annotations
from typing import Sequence
import open_webui.internal.db  # noqa: F401
import sqlalchemy as sa
from alembic import op
from open_webui.internal.db import JSONField
from open_webui.migrations.util import get_existing_tables, key_text, portable_string

revision: str = '7e5b5dc7342b'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
# Initial schema table declarations
_INITIAL_TABLES: list[tuple[str, list[sa.Column], list]] = [
    (
        'auth',
        [
            sa.Column('id', portable_string(), nullable=False),
            sa.Column('email', portable_string(), nullable=True),
            sa.Column('password', sa.Text(), nullable=True),
            sa.Column('active', sa.Boolean(), nullable=True),
        ],
        [sa.PrimaryKeyConstraint('id')],
    ),
    (
        'chat',
        [
            sa.Column('id', portable_string(), nullable=False),
            sa.Column('user_id', portable_string(), nullable=True),
            sa.Column('title', sa.Text(), nullable=True),
            sa.Column('chat', sa.Text(), nullable=True),
            sa.Column('created_at', sa.BigInteger(), nullable=True),
            sa.Column('updated_at', sa.BigInteger(), nullable=True),
            sa.Column('share_id', key_text(), nullable=True),
            sa.Column('archived', sa.Boolean(), nullable=True),
        ],
        [sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('share_id')],
    ),
    (
        'chatidtag',
        [
            sa.Column('id', portable_string(), nullable=False),
            sa.Column('tag_name', portable_string(), nullable=True),
            sa.Column('chat_id', portable_string(), nullable=True),
            sa.Column('user_id', portable_string(), nullable=True),
            sa.Column('timestamp', sa.BigInteger(), nullable=True),
        ],
        [sa.PrimaryKeyConstraint('id')],
    ),
    (
        'document',
        [
            sa.Column('collection_name', portable_string(), nullable=False),
            sa.Column('name', portable_string(), nullable=True),
            sa.Column('title', sa.Text(), nullable=True),
            sa.Column('filename', sa.Text(), nullable=True),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('user_id', portable_string(), nullable=True),
            sa.Column('timestamp', sa.BigInteger(), nullable=True),
        ],
        [sa.PrimaryKeyConstraint('collection_name'), sa.UniqueConstraint('name')],
    ),
    (
        'file',
        [
            sa.Column('id', portable_string(), nullable=False),
            sa.Column('user_id', portable_string(), nullable=True),
            sa.Column('filename', sa.Text(), nullable=True),
            sa.Column('meta', JSONField(), nullable=True),
            sa.Column('created_at', sa.BigInteger(), nullable=True),
        ],
        [sa.PrimaryKeyConstraint('id')],
    ),
    (
        'function',
        [
            sa.Column('id', portable_string(), nullable=False),
            sa.Column('user_id', portable_string(), nullable=True),
            sa.Column('name', sa.Text(), nullable=True),
            sa.Column('type', sa.Text(), nullable=True),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('meta', JSONField(), nullable=True),
            sa.Column('valves', JSONField(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('is_global', sa.Boolean(), nullable=True),
            sa.Column('updated_at', sa.BigInteger(), nullable=True),
            sa.Column('created_at', sa.BigInteger(), nullable=True),
        ],
        [sa.PrimaryKeyConstraint('id')],
    ),
    (
        'memory',
        [
            sa.Column('id', portable_string(), nullable=False),
            sa.Column('user_id', portable_string(), nullable=True),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('updated_at', sa.BigInteger(), nullable=True),
            sa.Column('created_at', sa.BigInteger(), nullable=True),
        ],
        [sa.PrimaryKeyConstraint('id')],
    ),
    (
        'model',
        [
            sa.Column('id', key_text(), nullable=False),
            sa.Column('user_id', key_text(), nullable=True),
            sa.Column('base_model_id', key_text(), nullable=True),
            sa.Column('name', sa.Text(), nullable=True),
            sa.Column('params', JSONField(), nullable=True),
            sa.Column('meta', JSONField(), nullable=True),
            sa.Column('updated_at', sa.BigInteger(), nullable=True),
            sa.Column('created_at', sa.BigInteger(), nullable=True),
        ],
        [sa.PrimaryKeyConstraint('id')],
    ),
    (
        'prompt',
        [
            sa.Column('command', portable_string(), nullable=False),
            sa.Column('user_id', portable_string(), nullable=True),
            sa.Column('title', sa.Text(), nullable=True),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('timestamp', sa.BigInteger(), nullable=True),
        ],
        [sa.PrimaryKeyConstraint('command')],
    ),
    (
        'tag',
        [
            sa.Column('id', portable_string(), nullable=False),
            sa.Column('name', portable_string(), nullable=True),
            sa.Column('user_id', portable_string(), nullable=True),
            sa.Column('data', sa.Text(), nullable=True),
        ],
        [sa.PrimaryKeyConstraint('id')],
    ),
    (
        'tool',
        [
            sa.Column('id', portable_string(), nullable=False),
            sa.Column('user_id', portable_string(), nullable=True),
            sa.Column('name', sa.Text(), nullable=True),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('specs', JSONField(), nullable=True),
            sa.Column('meta', JSONField(), nullable=True),
            sa.Column('valves', JSONField(), nullable=True),
            sa.Column('updated_at', sa.BigInteger(), nullable=True),
            sa.Column('created_at', sa.BigInteger(), nullable=True),
        ],
        [sa.PrimaryKeyConstraint('id')],
    ),
    (
        'user',
        [
            sa.Column('id', portable_string(), nullable=False),
            sa.Column('name', portable_string(), nullable=True),
            sa.Column('email', portable_string(), nullable=True),
            sa.Column('role', portable_string(), nullable=True),
            sa.Column('profile_image_url', sa.Text(), nullable=True),
            sa.Column('last_active_at', sa.BigInteger(), nullable=True),
            sa.Column('updated_at', sa.BigInteger(), nullable=True),
            sa.Column('created_at', sa.BigInteger(), nullable=True),
            sa.Column('api_key', portable_string(), nullable=True),
            sa.Column('settings', JSONField(), nullable=True),
            sa.Column('info', JSONField(), nullable=True),
            sa.Column('oauth_sub', key_text(), nullable=True),
        ],
        [
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('api_key'),
            sa.UniqueConstraint('oauth_sub'),
        ],
    ),
]


# --- migration execution ---
def upgrade() -> None:  # deploy initial schema tables
    existing_tables = set(get_existing_tables())
    for name, columns, constraints in _INITIAL_TABLES:
        if name not in existing_tables:
            op.create_table(name, *columns, *constraints)


# --- rollback function ---
def downgrade() -> None:  # rollback initial schema tables
    for table_name, _, _ in reversed(_INITIAL_TABLES):
        op.drop_table(table_name)
