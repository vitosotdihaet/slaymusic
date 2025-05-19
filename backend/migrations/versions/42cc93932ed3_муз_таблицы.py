from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '42cc93932ed3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    op.create_table(
        'artists',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_artist_name_gin_trgm', 'artists', ['name'], postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})

    op.create_table(
        'genres',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_genre_name_gin_trgm', 'genres', ['name'], postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})

    op.create_table(
        'albums',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('artist_id', sa.Integer(), nullable=False),
        sa.Column('release_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_album_name_gin_trgm', 'albums', ['name'], postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})

    op.create_table(
        'tracks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('album_id', sa.Integer(), nullable=False),
        sa.Column('artist_id', sa.Integer(), nullable=False),
        sa.Column('genre_id', sa.Integer(), nullable=True),
        sa.Column('release_date', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['album_id'], ['albums.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_track_name_gin_trgm', 'tracks', ['name'], postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})

def downgrade():
    op.drop_index('idx_track_name_gin_trgm', table_name='tracks')
    op.drop_table('tracks')

    op.drop_index('idx_album_name_gin_trgm', table_name='albums')
    op.drop_table('albums')

    op.drop_index('idx_genre_name_gin_trgm', table_name='genres')
    op.drop_table('genres')

    op.drop_index('idx_artist_name_gin_trgm', table_name='artists')
    op.drop_table('artists')