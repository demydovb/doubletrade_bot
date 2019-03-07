from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Airports(Base):
    __tablename__ = 'airports'
    id = Column(Integer, primary_key=True)
    iata_code = Column(String)
    city_name = Column(String)