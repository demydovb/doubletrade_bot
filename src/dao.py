from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, load_only
# from config import userdb, passdb, dbhost, dbname

Base = declarative_base()

engine = create_engine(
    'postgresql://{userdb}:{passdb}@{dbhost}/{dbname}'.format(userdb='demydovb', passdb='demydovb', dbhost='localhost', dbname='doubletrade'),
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
    session.add(Airports(iata_code=iata_code,city_name=city_name))
    session.commit()
    return True

