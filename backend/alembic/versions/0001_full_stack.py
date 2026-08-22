"""Create the full GlobeTrotter schema or upgrade the legacy trip schema.

Revision ID: 0001_full_stack
"""
from alembic import op
import sqlalchemy as sa

from backend import models  # noqa: F401
from backend.database import Base

revision = "0001_full_stack"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    if "trips" in tables:
        columns={c["name"] for c in sa.inspect(bind).get_columns("trips")}
        with op.batch_alter_table("trips") as batch:
            if "budget_limit" not in columns: batch.add_column(sa.Column("budget_limit",sa.Float()))
            if "created_at" not in columns: batch.add_column(sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
            if "updated_at" not in columns: batch.add_column(sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    Base.metadata.create_all(bind=bind)

def downgrade():
    Base.metadata.drop_all(bind=op.get_bind())
