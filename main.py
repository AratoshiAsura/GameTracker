from fastapi import Depends, FastAPI, HTTPException, status
from database import get_db, init_db
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Game
from schemas import GameCreate, GameResponse, GameUpdate, StatsResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    
app =FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(game: GameCreate, db: AsyncSession = Depends(get_db)):
    new_game=Game(**game.model_dump())
    db.add(new_game)
    await db.commit()
    await db.refresh(new_game)
    return new_game
    
@app.get("/games", response_model=list[GameResponse])
async def list_game(
    status_filter: str | None=None,
    platform: str | None=None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Game)
    if status_filter:
        query = query.where(Game.status == status_filter)
    if platform: 
        query = query.where(Game.platform == platform)
    result = await db.execute(query)
    return result.scalars().all()

@app.get("/games"{game}, response_model=list[GameResponse])
async def get_game(game_id: int, db: AsyncSession = Depends(get_db)):
    game = await db.get(Game,game_id)
    if game is None:
        raise HTTPException(status_code=status.HTTP_400_NOT_FOUND, detail="Game not found")
    return game