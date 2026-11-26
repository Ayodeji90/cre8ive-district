"""add_credit_balance_and_credit_transactions

Add credit_balance column to the businesses table and create the
credit_transactions ledger table.  Both existed in the ORM models since
launch but were never materialised by a migration.

The migration reconciles any existing ledger rows (should be none on a
fresh DB, but handles the edge case where application-level create_all was
used before migrations were applied):

  1.  Adds businesses.credit_balance with server_default=50.
  2.  Creates the credit_transactions table.
  3.  For each business that already has transactions, sets credit_balance
      to the balance_after of its most recent transaction.

Revision ID: g6c9d5e2f345
Revises: f5b8c4d1e234
Create Date: 2026-11-19 02:50:00.000000+00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "g6c9d5e2f345"
down_revision = "f5b8c4d1e234"
branch_labels = None
depends_on = None

json_type = sa.JSON().with_variant(JSONB(), "postgresql")


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    business_columns = [c["name"] for c in inspector.get_columns("businesses")]

    # --- 1. Add credit_balance to businesses if not present ---
    if "credit_balance" not in business_columns:
        op.add_column(
            "businesses",
            sa.Column(
                "credit_balance",
                sa.Integer(),
                nullable=False,
                server_default="50",
            ),
        )

    # --- 1b. Harmonize projects.business_id unique constraint / index for existing databases ---
    if "projects" in existing_tables:
        project_constraints = [c["name"] for c in inspector.get_unique_constraints("projects")]
        if "uq_projects_business_id" in project_constraints:
            op.drop_constraint("uq_projects_business_id", "projects", type_="unique")
        project_indexes = inspector.get_indexes("projects")
        for idx in project_indexes:
            if idx["name"] == "ix_projects_business_id" and not idx.get("unique"):
                op.drop_index("ix_projects_business_id", table_name="projects")
                op.create_index("ix_projects_business_id", "projects", ["business_id"], unique=True)

    # --- 2. Create the credit ledger if not present ---
    if "credit_transactions" not in existing_tables:
        op.create_table(
            "credit_transactions",
            sa.Column("id", sa.Uuid(), primary_key=True),
            sa.Column(
                "business_id",
                sa.Uuid(),
                sa.ForeignKey("businesses.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("amount", sa.Integer(), nullable=False),
            sa.Column("balance_after", sa.Integer(), nullable=False),
            sa.Column("transaction_type", sa.String(32), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("reference_id", sa.String(120), nullable=True, index=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    # --- 3. Reconcile balances from any pre-existing ledger rows ---
    # Set each business's balance to the balance_after of its most recent transaction.
    connection.execute(
        sa.text(
            """
            UPDATE businesses
            SET credit_balance = sub.balance_after
            FROM (
                SELECT DISTINCT ON (business_id)
                    business_id, balance_after
                FROM credit_transactions
                ORDER BY business_id, created_at DESC, id DESC
            ) sub
            WHERE businesses.id = sub.business_id
            """
        )
    )

    # --- 4. Backfill initial signup credits in ledger for businesses with no transactions ---
    # Generates a signup_bonus transaction so ledger and credit_balance stay 100% in sync.
    connection.execute(
        sa.text(
            """
            INSERT INTO credit_transactions (id, business_id, amount, balance_after, transaction_type, description, created_at, updated_at)
            SELECT 
                gen_random_uuid(),
                b.id,
                b.credit_balance,
                b.credit_balance,
                'signup_bonus',
                'Initial signup credit balance',
                COALESCE(b.created_at, now()),
                COALESCE(b.created_at, now())
            FROM businesses b
            LEFT JOIN credit_transactions ct ON ct.business_id = b.id
            WHERE ct.id IS NULL
            """
        )
    )


def downgrade() -> None:
    """Intentionally blocked — this migration manages customer credit data.

    Dropping ``credit_transactions`` and ``businesses.credit_balance`` would
    destroy customer payment history and balances irreversibly.

    **Recovery plan (manual only):**
      1. ``pg_dump --table=credit_transactions --table=businesses <db>``
         to export a full backup of both tables.
      2. Verify the backup can be restored on a scratch database.
      3. Only then run the downgrade manually:
            ALTER TABLE businesses DROP COLUMN credit_balance;
            DROP TABLE credit_transactions;
      4. Apply the backup if rollback was accidental.

    If you are absolutely certain this is a development database with no
    customer data, set the environment variable ``ALLOW_CREDIT_DOWNGRADE=1``
    before running ``alembic downgrade``.
    """
    import os

    if os.environ.get("ALLOW_CREDIT_DOWNGRADE") != "1":
        raise RuntimeError(
            "Downgrade blocked: this migration manages customer credit balances "
            "and transaction history. Dropping these tables would destroy "
            "customer data. Set ALLOW_CREDIT_DOWNGRADE=1 to override "
            "(development databases only). See the docstring for the full "
            "recovery plan."
        )
    op.drop_table("credit_transactions")
    op.drop_column("businesses", "credit_balance")
