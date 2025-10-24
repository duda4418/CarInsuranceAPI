"""baseline-database-migration

Revision ID: 379b63c92056
Revises:
Create Date: 2025-10-22 14:19:21.510876

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers.
revision: str = "379b63c92056"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "owner",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_owner")),
    )
    op.create_table(
        "car",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vin", sa.String(length=32), nullable=False),
        sa.Column("make", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("year_of_manufacture", sa.Integer(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["owner.id"],
            name=op.f("fk_car_owner_id_owner"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_car")),
    )
    op.create_index(op.f("ix_car_owner_id"), "car", ["owner_id"], unique=False)
    op.create_index(op.f("ix_car_vin"), "car", ["vin"], unique=True)
    op.create_table(
        "claim",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("car_id", sa.Integer(), nullable=False),
        sa.Column("claim_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["car_id"], ["car.id"], name=op.f("fk_claim_car_id_car"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_claim")),
    )
    op.create_index(op.f("ix_claim_car_id"), "claim", ["car_id"], unique=False)
    op.create_table(
        "insurance_policy",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("car_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("logged_expiry_at", postgresql.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(
            ["car_id"],
            ["car.id"],
            name=op.f("fk_insurance_policy_car_id_car"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_insurance_policy")),
    )
    op.create_index(
        op.f("ix_insurance_policy_car_id"), "insurance_policy", ["car_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_insurance_policy_car_id"), table_name="insurance_policy")
    op.drop_table("insurance_policy")
    op.drop_index(op.f("ix_claim_car_id"), table_name="claim")
    op.drop_table("claim")
    op.drop_index(op.f("ix_car_vin"), table_name="car")
    op.drop_index(op.f("ix_car_owner_id"), table_name="car")
    op.drop_table("car")
    op.drop_table("owner")
