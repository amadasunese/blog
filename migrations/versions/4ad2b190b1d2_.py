"""empty message

Revision ID: 4ad2b190b1d2
Revises: 44a54a232500
Create Date: 2024-08-04 18:32:42.437270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ad2b190b1d2'
down_revision = '44a54a232500'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_advertisement')
    with op.batch_alter_table('advertisement', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_posted', sa.DateTime(), nullable=True))
        batch_op.alter_column('image_file',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=20),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('advertisement', schema=None) as batch_op:
        batch_op.alter_column('image_file',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
        batch_op.drop_column('date_posted')

    op.create_table('_alembic_tmp_advertisement',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('embed_link', sa.VARCHAR(length=255), nullable=True),
    sa.Column('ad_code', sa.TEXT(), nullable=True),
    sa.Column('image_file', sa.VARCHAR(length=20), nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), nullable=True),
    sa.Column('date_posted', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
