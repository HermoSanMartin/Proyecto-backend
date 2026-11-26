"""Limita las solicitudes de recuperacion por cuenta."""

import sqlalchemy as sa
from alembic import op

revision = "b38d024fae10"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "usuarios", sa.Column("proxima_recuperacion", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade():
    op.drop_column("usuarios", "proxima_recuperacion")
