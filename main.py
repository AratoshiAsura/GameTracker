from fastapi import Depends, FastAPI, HTTPException, status
from database import get_db, init_db
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
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

@app.get("/games/{game_id}", response_model=GameResponse)
async def get_game(game_id: int, db: AsyncSession = Depends(get_db)):
    game = await db.get(Game,game_id)
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return game

@app.patch("/games/{game_id}", response_model=GameResponse)
async def update_game(
    game_id: int,
    data: GameUpdate,
    db: AsyncSession = Depends(get_db)
):
    game = await db.get(Game, game_id)

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(game, key, value)

    await db.commit()
    await db.refresh(game)

    return game

@app.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    game_id: int,
    db: AsyncSession = Depends(get_db)
):
    game = await db.get(Game, game_id)
    
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No contetnt"
        )

    await db.delete(game)
    await db.commit()

@app.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    status_result = await db.execute(
        select(Game.status, func.count(Game.id)).group_by(Game.status)
    )
    by_status = {status: count for status, count in status_result.all()}
    agg_result = await db.execute(
        select(func.avg(Game.rating), func.sum(Game.hours_played))
    )
    avg_rating, total_hours = agg_result.one()

    return StatsResponse(
        by_status = by_status,
        avg_rating = avg_rating or 0.0,
        total_hours = total_hours or 0.0,
    )