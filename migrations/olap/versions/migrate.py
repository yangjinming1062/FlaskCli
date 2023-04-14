"""
Description : 来自alembic自动生成的版本文件，因ClickHouse自动生成的脚本不佳因此改为执行预设的脚本
"""
import os

from alembic import op

# revision identifiers, used by Alembic.
revision = 'c2be2eef164d'
down_revision = None
branch_labels = None
depends_on = None
current_dir = os.path.dirname(os.path.realpath(__file__))


def upgrade() -> None:
    with open(os.path.join(current_dir, 'upgrade.sql'), 'r') as f:
        content = f.read()
    for statement in content.split(';'):
        statement = statement.strip(' \n')
        if statement:
            op.execute(statement)


def downgrade() -> None:
    with open(os.path.join(current_dir, 'downgrade.sql'), 'r') as f:
        content = f.read()
    for statement in content.split(';'):
        statement = statement.strip(' \n')
        if statement:
            op.execute(statement)
