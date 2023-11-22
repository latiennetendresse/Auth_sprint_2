"""session_jti

Revision ID: aab9f2f39b08
Revises: 83ac4486af09
Create Date: 2023-07-19 13:34:59.934092

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "aab9f2f39b08"
down_revision = "83ac4486af09"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "sessions",
        sa.Column("access_jti", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "sessions",
        sa.Column("refresh_jti", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.drop_column("sessions", "access_token")
    op.drop_column("sessions", "refresh_token")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "sessions",
        sa.Column("refresh_token", sa.TEXT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "sessions",
        sa.Column("access_token", sa.TEXT(), autoincrement=False, nullable=True),
    )
    op.drop_column("sessions", "refresh_jti")
    op.drop_column("sessions", "access_jti")
    # ### end Alembic commands ###
