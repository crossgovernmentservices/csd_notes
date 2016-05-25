"""empty message

Revision ID: a51bfef2da80
Revises: 560f5b030416
Create Date: 2016-05-13 14:37:51.418417

"""

# revision identifiers, used by Alembic.
revision = 'a51bfef2da80'
down_revision = '560f5b030416'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_tag_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tag'))
    )
    op.create_table('note_tag',
    sa.Column('tag.id', sa.Integer(), nullable=True),
    sa.Column('note.id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['note.id'], ['note.id'], name=op.f('fk_note_tag_note.id_note')),
    sa.ForeignKeyConstraint(['tag.id'], ['tag.id'], name=op.f('fk_note_tag_tag.id_tag'))
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('note_tag')
    op.drop_table('tag')
    ### end Alembic commands ###