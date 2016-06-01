"""empty message

Revision ID: 8d72bd69bf21
Revises: 1672e12c53dd
Create Date: 2016-06-01 16:37:55.869479

"""

# revision identifiers, used by Alembic.
revision = '8d72bd69bf21'
down_revision = '1672e12c53dd'

from alembic import op
import sqlalchemy as sa


tag = sa.Table(
    'tag',
    sa.MetaData(),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String),
    sa.Column('namespace', sa.String),
    sa.Column('user_id', sa.Integer)
)


system_tag_names = [
    'development',
    'email',
    'feedback']


def upgrade():
    for name in system_tag_names:
        op.execute(tag.insert().values(namespace='System', name=name))


def downgrade():
    for name in system_tag_names:
        op.execute(tag.delete().where(sa.and_(
            tag.c.namespace == 'System',
            tag.c.name == name)))
