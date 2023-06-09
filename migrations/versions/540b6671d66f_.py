"""empty message

Revision ID: 540b6671d66f
Revises: 917ee3d4506c
Create Date: 2023-05-01 02:26:53.690431

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '540b6671d66f'
down_revision = '917ee3d4506c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('favorite_food', sa.String(length=200), nullable=True))
        batch_op.drop_column('organization')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('organization', mysql.VARCHAR(length=200), nullable=True))
        batch_op.drop_column('favorite_food')

    # ### end Alembic commands ###
