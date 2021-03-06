"""create comment table

Revision ID: 3ee47a319b67
Revises: 
Create Date: 2018-12-03 11:50:35.831781

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ee47a319b67'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_ip', sa.String(length=64), nullable=True),
    sa.Column('user_agent', sa.String(length=256), nullable=True),
    sa.Column('referrer', sa.String(length=256), nullable=True),
    sa.Column('comment_type', sa.String(length=32), nullable=True),
    sa.Column('comment_author', sa.String(length=64), nullable=True),
    sa.Column('comment_author_email', sa.String(length=128), nullable=True),
    sa.Column('comment_content', sa.String(length=512), nullable=True),
    sa.Column('website', sa.String(length=64), nullable=True),
    sa.Column('slug', sa.String(length=128), nullable=True),
    sa.Column('post_url', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comment')
    # ### end Alembic commands ###
