from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    service: Literal["UP"]
    database: Literal["UP", "DOWN"]
