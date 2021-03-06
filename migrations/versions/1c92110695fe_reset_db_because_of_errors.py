"""Reset DB because of errors

Revision ID: 1c92110695fe
Revises: 
Create Date: 2021-05-05 04:53:41.232174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c92110695fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('echo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('echo_id', sa.String(length=256), nullable=True),
    sa.Column('code', sa.Integer(), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('echo_id'),
    sa.UniqueConstraint('echo_id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('grades_password', sa.Integer(), nullable=True),
    sa.Column('echo', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['echo'], ['echo.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    op.drop_table('echo')
    # ### end Alembic commands ###
