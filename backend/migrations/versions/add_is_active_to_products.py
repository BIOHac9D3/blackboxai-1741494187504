"""add is_active to products

Revision ID: add_is_active_to_products
Revises: 93a0b060fa16
Create Date: 2025-03-21 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_is_active_to_products'
down_revision = '93a0b060fa16'
branch_labels = None
depends_on = None

def upgrade():
    # Add is_active column with default value True
    op.add_column('products', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))

def downgrade():
    # Remove is_active column
    op.drop_column('products', 'is_active')
