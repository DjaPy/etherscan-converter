from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class StatusTrXEnum(Enum):
    success = 'success'
    fail = 'fail'


class TrxDetail(BaseModel):
    trx_hash: bytes
    status: StatusTrXEnum
    date: datetime
    block_id: int
    date: datetime
    from_trx: bytes
    to: bytes
    partner: Optional[str]
    trx_fee: Decimal
