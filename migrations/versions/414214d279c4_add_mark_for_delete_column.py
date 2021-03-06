"""add mark_for_delete column

Revision ID: 414214d279c4
Revises: b1acb7c5f9bf
Create Date: 2018-12-03 13:56:09.616323

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '414214d279c4'
down_revision = 'b1acb7c5f9bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('mark_for_delete', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comment', 'mark_for_delete')
    # ### end Alembic commands ###
