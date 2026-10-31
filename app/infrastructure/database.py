from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.config import configuracion

engine = create_engine(configuracion.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)