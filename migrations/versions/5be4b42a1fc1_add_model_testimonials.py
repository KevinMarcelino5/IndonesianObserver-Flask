"""add model.Testimonials

Revision ID: 5be4b42a1fc1
Revises: 482ad0cd836e
Create Date: 2023-05-08 01:13:35.168354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5be4b42a1fc1'
down_revision = '482ad0cd836e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('testimonials',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('date_posted', sa.DateTime(), nullable=True),
    sa.Column('penulis_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['penulis_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('testimonials')
    # ### end Alembic commands ###
