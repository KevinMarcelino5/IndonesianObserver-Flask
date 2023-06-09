"""added password field

Revision ID: 71afb7fb81f8
Revises: 345e52cd52c2
Create Date: 2023-04-26 14:01:30.236486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71afb7fb81f8'
down_revision = '345e52cd52c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('password_hash')

    # ### end Alembic commands ###
