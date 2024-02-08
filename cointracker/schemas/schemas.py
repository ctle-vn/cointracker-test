import re
from typing import Dict, List, Optional
from pydantic import BaseModel, RootModel, Field, field_validator
from datetime import datetime


class Transaction(BaseModel):
    hash: str
    amount: float
    sender: str
    receiver: str
    time: datetime


class BitcoinAddress(BaseModel):
    address: str
    user_id: str
    transactions: Optional[Transaction] = []
    balance: Optional[float] = 0.0
