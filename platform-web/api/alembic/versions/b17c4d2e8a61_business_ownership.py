"""Persist business ownership for authenticated workspaces."""

from datetime import UTC, datetime
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy import bindparam


revision: str = "b17c4d2e8a61"
down_revision: str | None = "a09c68f54b21"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("businesses", sa.Column("owner_id", sa.Uuid(), nullable=True))

    connection = op.get_bind()
    # Keep legacy workspaces with their most recent authenticated conversation owner.
    connection.execute(
        sa.text(
            """
            UPDATE businesses
            SET owner_id = (
                SELECT conversations.user_id
                FROM conversations
                WHERE conversations.business_id = businesses.id
                  AND conversations.user_id IS NOT NULL
                ORDER BY conversations.created_at DESC, conversations.id DESC
                LIMIT 1
            )
            WHERE owner_id IS NULL
            """
        )
    )

    unowned_count = connection.scalar(
        sa.text("SELECT count(*) FROM businesses WHERE owner_id IS NULL")
    )
    if unowned_count:
        # Preserve legacy businesses that have no linked user conversation under a
        # reserved, non-login owner rather than guessing a real customer's identity.
        fallback_id = uuid.uuid5(uuid.NAMESPACE_URL, "cre8ive-district:legacy-business-owner")
        fallback_email = "legacy-business-owner@cre8ivedistrict.invalid"
        existing_id = connection.scalar(
            sa.text("SELECT id FROM users WHERE email = :email"), {"email": fallback_email}
        )
        if existing_id is None:
            now = datetime.now(UTC)
            connection.execute(
                sa.text(
                    """
                    INSERT INTO users (id, email, name, role, avatar_url, created_at, updated_at)
                    VALUES (:id, :email, :name, :role, NULL, :created_at, :updated_at)
                    """
                ).bindparams(bindparam("id", type_=sa.Uuid())),
                {
                    "id": fallback_id,
                    "email": fallback_email,
                    "name": "Legacy business owner",
                    "role": "customer",
                    "created_at": now,
                    "updated_at": now,
                },
            )
        else:
            fallback_id = existing_id
        connection.execute(
            sa.text("UPDATE businesses SET owner_id = :owner_id WHERE owner_id IS NULL").bindparams(
                bindparam("owner_id", type_=sa.Uuid())
            ),
            {"owner_id": fallback_id},
        )

    with op.batch_alter_table("businesses") as batch_op:
        batch_op.alter_column("owner_id", existing_type=sa.Uuid(), nullable=False)
        batch_op.create_foreign_key(
            "fk_businesses_owner_id_users", "users", ["owner_id"], ["id"], ondelete="CASCADE"
        )
    op.create_index("ix_businesses_owner_id", "businesses", ["owner_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_businesses_owner_id", table_name="businesses")
    with op.batch_alter_table("businesses") as batch_op:
        batch_op.drop_constraint("fk_businesses_owner_id_users", type_="foreignkey")
        batch_op.drop_column("owner_id")
