from sqlalchemy.orm import declarative_base

Base = declarative_base()

from db.models import user
from db.models import parking_lot
from db.models import parking_session
from db.models import reservation
from db.models import vehicle
