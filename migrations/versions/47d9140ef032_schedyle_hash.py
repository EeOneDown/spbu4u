"""schedyle_hash

Revision ID: 47d9140ef032
Revises: 1f44305f4402
Create Date: 2018-10-18 22:53:50.152525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47d9140ef032'
down_revision = '1f44305f4402'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('educators', sa.Column('schedule_hash', sa.String(length=128), nullable=True))
    op.add_column('groups', sa.Column('schedule_hash', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('groups', 'schedule_hash')
    op.drop_column('educators', 'schedule_hash')
    # ### end Alembic commands ###