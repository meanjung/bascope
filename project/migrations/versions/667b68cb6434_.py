"""empty message

Revision ID: 667b68cb6434
Revises: df0f70e18b36
Create Date: 2021-10-08 20:44:54.654422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '667b68cb6434'
down_revision = 'df0f70e18b36'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('report', sa.Column('result', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('report', 'result')
    # ### end Alembic commands ###