from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Создаем файл базы данных (zhuki.db)
DATABASE_URL = "sqlite:///./zhuki.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель игрока (таблица в БД)
class Player(Base):
    __tablename__ = "players"

    tg_id = Column(Integer, primary_key=True, index=True) # ID из Телеграма
    username = Column(String, default="BeetleKeeper")
    
    # Ресурсы
    money = Column(Integer, default=100)      # Багсы
    
    # Параметры Жука
    beetle_name = Column(String, default="Жучара")
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    
    hunger = Column(Float, default=50.0)      # 0..100
    strength = Column(Float, default=1.0)
    
    last_login = Column(DateTime, default=datetime.utcnow)

# Создаем таблицы, если их нет
Base.metadata.create_all(bind=engine)
