from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import conf
from urllib.parse import quote_plus



SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{conf.user}:{quote_plus(conf.password)}@{conf.host}:{conf.port}/{conf.database}?charset=utf8mb4"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()