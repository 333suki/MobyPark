from sqlalchemy import create_engige
from sqlalchemy.orm import sessionmaker
from core.config import settings

engine = create_engige(
    settings.DATABASE_URL,
    connect_args=("check_same_thread": False),
    echo=True
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)