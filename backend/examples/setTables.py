from sqlalchemy import Column, Integer, String, text
from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session


engine = create_engine('postgresql+psycopg2://postgres:123@localhost:5432/mori')

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column("name", String)
    email = Column("email", String)
    password = Column("password", String)

Base.metadata.create_all(engine)

with Session(engine) as session:
    user = session.query(User).first() #.filter_by(id=3)
    print(user.name)