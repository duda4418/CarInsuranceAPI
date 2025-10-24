"""
Task A: Populate end_date where NULL, then set NOT NULL
Add composite indexes for insurance_policy and claim

Revision ID: taska_enddate_notnull
Revises: 379b63c92056
Create Date: 2025-10-22
"""

import sqlalchemy as sa
from sqlalchemy import Date, func
from sqlalchemy.sql import column, table

from alembic import op

# revision identifiers.
revision = "taska_enddate_notnull"
down_revision = "379b63c92056"
branch_labels = None
depends_on = None


def upgrade():
    # set end_date where NULL
    insurance_policy = table(
        "insurance_policy",
        column("id", sa.Integer),
        column("start_date", Date),
        column("end_date", Date),
    )
    op.execute(
        insurance_policy.update()
        .where(insurance_policy.c.end_date == None)
        .values(end_date=func.DATE(sa.text("start_date + INTERVAL '1 year'")))
    )
    # end_date to NOT NULL
    op.alter_column("insurance_policy", "end_date", nullable=False)
    # composite indexes
    op.create_index(
        "ix_insurance_policy_car_id_start_date_end_date",
        "insurance_policy",
        ["car_id", "start_date", "end_date"],
        unique=False,
    )
    op.create_index(
        "ix_claim_car_id_claim_date", "claim", ["car_id", "claim_date"], unique=False
    )


def downgrade():
    op.drop_index("ix_claim_car_id_claim_date", table_name="claim")
    op.drop_index(
        "ix_insurance_policy_car_id_start_date_end_date", table_name="insurance_policy"
    )
    op.alter_column("insurance_policy", "end_date", nullable=True)
    # No data rollback for end_date
