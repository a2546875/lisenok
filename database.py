from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

from config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    auth_provider = Column(String)  # vk, google, mail, max
    is_admin = Column(Boolean, default=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    retail_price = Column(Float)
    wholesale_price = Column(Float)
    image_url = Column(String)
    is_active = Column(Boolean, default=True)


class ConstructorOption(Base):
    __tablename__ = "constructor_options"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)  # 'set_type', 'color', 'pattern'
    name = Column(String)


class Inquiry(Base):
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    contact = Column(String)
    message = Column(Text)
    design = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
