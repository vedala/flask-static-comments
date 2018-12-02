"""add slug column

Revision ID: 4f0a4a445825
Revises: 8881697f180a
Create Date: 2018-12-02 05:13:05.689000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f0a4a445825'
down_revision = '8881697f180a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('slug', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comment', 'slug')
    # ### end Alembic commands ###
