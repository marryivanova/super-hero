from sqlalchemy import Column, Integer, String, Float

from src.db.data_base import Base


class Hero(Base):
    __tablename__ = "heroes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    intelligence = Column(Float)
    strength = Column(Float)
    speed = Column(Float)
    power = Column(Float)

    full_name = Column(String)
    publisher = Column(String)
    alignment = Column(String)
    image_url = Column(String)
