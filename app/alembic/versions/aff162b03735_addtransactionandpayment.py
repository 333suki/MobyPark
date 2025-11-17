"""AddTransactionAndPayment

Revision ID: aff162b03735
Revises: e8247ae285d2
Create Date: 2025-11-11 10:47:45.844875
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'aff162b03735'
down_revision: Union[str, Sequence[str], None] = 'e8247ae285d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('method', sa.String, nullable=False),
        sa.Column('issuer', sa.String, nullable=False),
        sa.Column('bank', sa.String, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'payments',
        sa.Column('transaction', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('initiator_id', sa.Integer, nullable=False),
        sa.Column('created_at', sa.Date, nullable=False),
        sa.Column('completed', sa.Date, nullable=False),
        sa.Column('hash', sa.String, nullable=False),
        sa.Column('t_data_id', sa.Integer, nullable=False),
        sa.Column('parking_session_id', sa.Integer, nullable=False),
        sa.Column('parking_lot_id', sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(['initiator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['t_data_id'], ['transactions.id'], ),
        sa.ForeignKeyConstraint(['parking_session_id'],['parking_sessions.id'], ),
        sa.ForeignKeyConstraint(['parking_lot_id'],['parking_lots.id'], ),
        sa.PrimaryKeyConstraint('transaction')
    )

def downgrade() -> None:
    op.drop_table('payments')
    op.drop_table('transactions')
