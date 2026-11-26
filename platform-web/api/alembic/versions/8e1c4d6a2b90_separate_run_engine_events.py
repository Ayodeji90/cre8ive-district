"""separate Run Engine events from platform events

Rename the Run Engine's legacy ``run_events`` table before the platform
migration creates its own table with the same name.

Revision ID: 8e1c4d6a2b90
Revises: c21a6e8f4d90
"""

from alembic import op
import sqlalchemy as sa

revision = "8e1c4d6a2b90"
down_revision = "c21a6e8f4d90"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = set(inspector.get_table_names())

    if "run_events" not in tables:
        return

    columns = {column["name"] for column in inspector.get_columns("run_events")}
    if "run_id" not in columns or "agent_run_id" in columns:
        raise RuntimeError(
            "Cannot safely rename run_events: expected the legacy Run Engine schema "
            "with run_id, but found a different table shape."
        )
    if "run_engine_events" in tables:
        raise RuntimeError(
            "Cannot rename legacy run_events because run_engine_events already exists."
        )

    op.rename_table("run_events", "run_engine_events")


def downgrade() -> None:
    raise RuntimeError("This migration is forward-only; restore the database from backup instead.")
