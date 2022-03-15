from pydantic import BaseModel, Field

from etherscan_converter.enums import HealthStatus


class HealthResponseSchema(BaseModel):
    status: HealthStatus = HealthStatus.ok
    s3: HealthStatus = HealthStatus.ok
    version: str = Field(description='app version')
