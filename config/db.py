from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool  # optional

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL is not set in environment variables")

engine = create_engine(
    database_url,
    pool_size=10,          # number of persistent connections
    max_overflow=5,        # allow some spikes
    pool_timeout=30,       # wait for a free connection before error
    pool_recycle=1800,     # recycle every 30 min to avoid "MySQL server has gone away"
    pool_pre_ping=True,    # validate connections before using
    echo=False             # set to True only for debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
