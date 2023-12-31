"""Initia migration

Revision ID: 3b8d366b4900
Revises: 
Create Date: 2023-06-27 01:21:26.884999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b8d366b4900'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('access_token', sa.String(), nullable=True))
        batch_op.drop_constraint('user_api_key_key', type_='unique')
        batch_op.create_unique_constraint(None, ['id'])
        batch_op.create_unique_constraint(None, ['access_token'])
        batch_op.drop_column('api_key')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('api_key', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_unique_constraint('user_api_key_key', ['api_key'])
        batch_op.drop_column('access_token')

    # ### end Alembic commands ###
