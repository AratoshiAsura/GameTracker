from typing import Literal

class GameCreate(BaseModel):
    title: str
    platform: str
    status: Literal["backlog", "playing", "completed", "dropped"] = "backlog"
    rating: int | None = Field(default=None, ge=1, le=10)
    hours_played: float = 0.0