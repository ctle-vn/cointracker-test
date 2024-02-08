from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import exists

Base = declarative_base()


class BitcoinAddressModel(Base):
    __tablename__ = "bitcoin_address"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True)
    user_id = Column(String, default="user_a")
    balance = Column(Float, default=0.0)

    transaction = relationship("TransactionModel", back_populates="bitcoin_address")


class TransactionModel(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String, unique=True, index=True)
    amount = Column(Float)
    sender = Column(String)
    receiver = Column(String)
    time = Column(DateTime)
    bitcoin_address_id = Column(Integer, ForeignKey("bitcoin_address.id"))

    bitcoin_address = relationship("BitcoinAddressModel", back_populates="transaction")
