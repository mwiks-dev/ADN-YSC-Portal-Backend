from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)
conn = engine.connect()

Base = declarative_base()

