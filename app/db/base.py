from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.db.models import user
from app.db.models import parking_lot
from app.db.models import parking_session
from app.db.models import reservation
from app.db.models import vehicle
