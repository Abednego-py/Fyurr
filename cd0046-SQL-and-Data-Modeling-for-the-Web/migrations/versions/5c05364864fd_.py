"""empty message

Revision ID: 5c05364864fd
Revises: b4a2a2fd609d
Create Date: 2022-05-25 06:18:09.733726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c05364864fd'
down_revision = 'b4a2a2fd609d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Shows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.String(length=120), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Shows')
    # ### end Alembic commands ###
