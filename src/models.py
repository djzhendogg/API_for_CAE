from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Keys(Base):
    __tablename__ = "keys"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
