"""empty message

Revision ID: ce32d8b7f976
Revises: 1c92110695fe
Create Date: 2021-05-05 13:05:42.095481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce32d8b7f976'
down_revision = '1c92110695fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('token', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'token')
    # ### end Alembic commands ###
