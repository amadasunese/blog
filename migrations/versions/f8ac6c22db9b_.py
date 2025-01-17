"""empty message

Revision ID: f8ac6c22db9b
Revises: e285c577f59a
Create Date: 2024-08-06 09:39:37.369011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8ac6c22db9b'
down_revision = 'e285c577f59a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('advertisement', schema=None) as batch_op:
        batch_op.add_column(sa.Column('location', sa.String(length=100), nullable=True))
        batch_op.alter_column('date_posted',
               existing_type=sa.DATETIME(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('advertisement', schema=None) as batch_op:
        batch_op.alter_column('date_posted',
               existing_type=sa.DATETIME(),
               nullable=True)
        batch_op.drop_column('location')

    # ### end Alembic commands ###
