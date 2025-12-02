from pathlib import Path
import sys
import os
import shutil
import atexit
import tempfile

# Adjust the path to include the app directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'app'))

# Copy the original testdatabase.db to a temporary location for testing.
# This ensures the original database stays consistent across test runs and versions.
ORIGINAL_DB_PATH = Path(__file__).resolve().parent.parent / 'app' / 'testdatabase.db'
TEMP_DIR = tempfile.mkdtemp(prefix='mobypark_test_')
TEST_DB_PATH = Path(TEMP_DIR) / 'testdatabase.db'

try:
	if ORIGINAL_DB_PATH.exists():
		shutil.copy2(ORIGINAL_DB_PATH, TEST_DB_PATH)
except Exception:
	# If copy fails, create a fresh one from scratch
	pass

os.environ['DATABASE_URL'] = f"sqlite:///{TEST_DB_PATH}"

# Register cleanup to remove temp directory after tests complete
def _cleanup_temp_db():
	try:
		if Path(TEMP_DIR).exists():
			shutil.rmtree(TEMP_DIR)
	except Exception:
		pass

atexit.register(_cleanup_temp_db)

# Creates the models tables in the test database if they don't exist yet.
try:
	# Alembic migrations are optional; if the copied DB exists with correct schema,
	# we skip migrations to preserve test data integrity.
	from alembic.config import Config
	from alembic import command
	from app.db.database import engine
	from app.db.base import Base

	# Only run migrations if the database doesn't already have tables
	# (i.e., if copy failed or original DB didn't exist).
	from sqlalchemy import inspect
	inspector = inspect(engine)
	if not inspector.get_table_names():
		alembic_cfg = Config(str(Path(__file__).resolve().parent.parent / 'app' / 'alembic.ini'))
		alembic_cfg.set_main_option('sqlalchemy.url', os.environ.get('DATABASE_URL', ''))
		try:
			command.upgrade(alembic_cfg, 'head')
		except Exception:
			Base.metadata.create_all(bind=engine)
except Exception:
	# If imports fail, avoid raising; let pytest report any actual test failures.
	pass