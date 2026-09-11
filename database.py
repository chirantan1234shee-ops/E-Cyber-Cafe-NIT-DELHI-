# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///yojna_mitra.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)  # In production, use bcrypt
    aadhaar_hash = Column(String, unique=True, index=True, nullable=True)
    name = Column(String)
    age = Column(Integer)
    annual_income = Column(Float)
    state = Column(String)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Scheme(Base):
    __tablename__ = "schemes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String)
    description = Column(String)
    rules = Column(JSON)  # min_age, max_age, max_income, allowed_states, eligible_categories
    is_active = Column(Boolean, default=True)

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    scheme_id = Column(Integer)
    status = Column(String)
    payload_snapshot = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()