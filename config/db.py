from sqlalchemy import create_engine
import os

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)
conn = engine.connect()