from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ServiceCreate(BaseModel):
    """Data accepted when a client creates a service."""

    name: str = Field(min_length=1, max_length=100)
    url: HttpUrl
    check_interval: int = Field(gt=0, description="Seconds between two checks")


class ServiceRead(BaseModel):
    """Data returned by the API for a service."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    check_interval: int
    created_at: datetime
