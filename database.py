from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./zhuki.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    tg_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, default="BeetleKeeper")
    money = Column(Integer, default=100)
    beetle_name = Column(String, default="Жучара")
    level = Column(Integer, default=1)
    hunger = Column(Float, default=50.0)
    strength = Column(Float, default=1.0)

Base.metadata.create_all(bind=engine)