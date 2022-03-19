from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from etherscan_converter.enums import HealthStatus


class HealthResponseSchema(BaseModel):
    status: HealthStatus = HealthStatus.ok
    s3: HealthStatus = HealthStatus.ok
    version: str = Field(description='app version')


class StatusTrXEnum(Enum):
    success = 'success'
    fail = 'fail'


class TrxDetail(BaseModel):
    trx_hash: bytes
    status: StatusTrXEnum
    date: datetime
    block_id: int
    from_trx: bytes
    to: bytes
    partner: Optional[str]
    trx_fee: Decimal
