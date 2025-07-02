from sqlalchemy import Column, Integer, String
from config.db import Base

class Deanery(Base):
    __tablename__ = "deaneries"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100))
    