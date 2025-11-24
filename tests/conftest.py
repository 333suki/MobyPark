from pathlib import Path
import sys
import os

# Adjust the path to include the app directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'app'))

# Gets the path to the test database file
TEST_DB_PATH = Path(__file__).resolve().parent.parent / 'testdatabase.db'
os.environ['DATABASE_URL'] = f"sqlite:///{TEST_DB_PATH}"

# Creates the models tables in the test database if they don't exist yet.
try:
	# Prefer running Alembic migrations so the test DB matches production schema.
	from alembic.config import Config
	from alembic import command
	from app.db.database import engine
	from app.db.base import Base

	alembic_cfg = Config(str(Path(__file__).resolve().parent.parent / 'app' / 'alembic.ini'))
	# Ensure alembic uses the same DATABASE_URL we set for tests
	alembic_cfg.set_main_option('sqlalchemy.url', os.environ.get('DATABASE_URL', ''))
	try:
		command.upgrade(alembic_cfg, 'head')
	except Exception:
		# If alembic fails for any reason, fall back to creating tables directly.
		Base.metadata.create_all(bind=engine)
except Exception:
	# If imports fail, avoid raising here to preserve pytest error reporting.
	pass