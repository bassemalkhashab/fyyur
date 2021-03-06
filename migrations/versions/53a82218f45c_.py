"""empty message

Revision ID: 53a82218f45c
Revises: 2a8ab6c4c8e2
Create Date: 2021-02-23 17:27:28.457676

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53a82218f45c'
down_revision = '2a8ab6c4c8e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###
