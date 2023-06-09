"""added foreign key

Revision ID: b5529faf2598
Revises: 250b672213ad
Create Date: 2023-05-01 13:03:57.082857

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b5529faf2598'
down_revision = '250b672213ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('journals', schema=None) as batch_op:
        batch_op.add_column(sa.Column('penulis_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'users', ['penulis_id'], ['id'])
        batch_op.drop_column('author')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('journals', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author', mysql.VARCHAR(length=255), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('penulis_id')

    # ### end Alembic commands ###
