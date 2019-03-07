from models import *
from sqlalchemy.orm import sessionmaker, load_only
from sqlalchemy import create_engine
from config import logindb, passdb, dbhost, dbname

engine = create_engine(
    f'postgresql://{logindb}:{passdb}@{dbhost}/{dbname}',
    echo=True)

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)

session = Session()

def add_airport_to_db(iata_code, city_name):
    session.add(Airports(iata_code=iata_code,city_name=iata_code))
    session.commit()

def get_airport_by_iata_code(iata_code):
    airport = session.query(Airports) \
        .filter(Airports.iata_code == iata_code) \
        .first()
    return airport.city_name