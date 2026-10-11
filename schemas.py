from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
from datetime import datetime

class GameBase(BaseModel):
    title: str
    platform: str
    status: Literal["backlog", "playing", "completed", "dropped"] = "backlog"
    rating: int | None = Field(default=None, ge=1, le=10)
    hours_played: float = 0.0

class GameCreate(GameBase):
    pass

class GameUpdate(BaseModel):
    title: str | None=None
    platform: str | None=None
    status: Literal["backlog", "playing", "completed", "dropped"] | None=None
    rating: int | None = Field(default=None, ge=1, le=10)
    hours_played: float | None=None

class GameResponse(GameBase):
    id:int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StatsResponse(BaseModel):
    by_status:dict[str, int]
    avg_rating: float | None
    total_hours: float