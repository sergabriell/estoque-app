from app.database.connection import Base, engine
from app.database import models  # noqa: F401

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
