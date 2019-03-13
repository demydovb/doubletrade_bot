import os

from functools import lru_cache
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine(
    'postgresql://{userdb}:{passdb}@{dbhost}/{dbname}'.format(
        userdb=os.getenv('USERDB'), passdb=os.getenv('PASSDB'),
        dbhost=os.getenv('DBHOST'), dbname=os.getenv('DBNAME')
    ),
    echo=True)

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)

session = Session()

class Airports(Base):
    __tablename__ = 'airports'
    id = Column(Integer, primary_key=True)
    iata_code = Column(String)
    city_name = Column(String)

Base.metadata.create_all(engine)


@lru_cache(maxsize=10)
def get_airport_by_iata_code(iata_code):
    airport = session.query(Airports) \
        .filter(Airports.iata_code == iata_code) \
        .first()
    if airport:
        return airport.city_name
    else:
        return False

def add_airport_to_database(iata_code, city_name):
    airport = get_airport_by_iata_code(iata_code)
    if airport:
        return False
    get_airport_by_iata_code.cache_clear() # We don't need cache results when add airport to db
    session.add(Airports(iata_code=iata_code,city_name=city_name))
    session.commit()
    return True

