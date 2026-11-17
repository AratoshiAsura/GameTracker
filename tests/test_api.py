import pytest
from unittest.mock import AsyncMock, patch
import json

@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_create_game(client):
    response = await client.post(
        "/games",
        json = {"title": "Test Game", "platform": "PC"},
        
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Game"
    assert "id" in data 
    assert "created_at" in data
    assert data["status"] == "backlog"
    
@pytest.mark.asyncio
async def test_create_game_validation_error(client):
    response = await client.post(
        "/games",
        json={"title": "Test Game", "platform": "PC", "rating": 11}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_game_by_id(client):
    create_resp = await client.post(
        "/games",
        json = {"title": "Cyberpunk 2077", "platform": "PC"}
    )

    game_id = create_resp.json()["id"]

    get_resp = await client.get(f"/games/{game_id}")

    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Cyberpunk 2077"

    not_found_resp = await client.get("/games/99999")
    assert not_found_resp.status_code == 404

@pytest.mark.asyncio
async def test_get_game_list(client):
    create_resp = await client.post(
        "/games",
        json = {"title": "Factorio", "platform": "PC"}
    )
    create_resp = await client.post(
        "/games",
        json = {"title": "Skyrim", "platform": "PC"}
    )

    response = await client.get("/games")
    
    assert response.status_code == 200

    games_list = response.json()

    assert isinstance(games_list, list)
    assert len(games_list) == 2

@pytest.mark.asyncio
async def test_get_game_empty(client):

    response = await client.get("/games")
    
    assert response.status_code == 200
    assert response.json() == []
  
@pytest.mark.asyncio
async def test_patch_gmae(client):
    create_resp = await client.post(
        "/games",
        json = {"title": "Tiny Bunny", "platform": "PC"}
    )
    game_id = create_resp.json()["id"]
    patch_resp = await client.patch(
        f"/games/{game_id}",
        json={"status": "completed", "rating": 9}
    )
    assert patch_resp.status_code == 200

    data = patch_resp.json()
    assert data["status"] == "completed"
    assert data["rating"] == 9

    assert data["title"] == "Tiny Bunny"
    assert data["platform"] == "PC"

@pytest.mark.asyncio
async def test_delete_game(client):
    create_resp = await client.post(
        "/games",
        json={"title": "World of goo", "platform": "PC"}
    )
    assert create_resp.status_code == 201
    game_id = create_resp.json()["id"]
    delete_resp = await client.delete(f"/games/{game_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/games/{game_id}")
    assert get_resp.status_code == 404

    delete_missing = await client.delete("/games/99999")
    assert delete_missing.status_code == 404

@pytest.mark.asyncio
async def test_stats(client):
    resp1 = await client.post(
        "/games",
        json={
            "title": "Game 1",
            "platform": "PC",
            "status": "playing",
            "rating": 10,
            "hours_played": 10.0,
        }
    )
    assert resp1.status_code == 201

    resp2 = await client.post(
        "/games",
        json={
            "title": "Game 2",
            "platform": "PC",
            "status": "playing",
            "hours_played": 5.0,
        }
    )
    assert resp2.status_code == 201

    
    response = await client.get("/stats")
    assert response.status_code == 200

    data = response.json()
    assert data["by_status"] == {"playing": 2}
    assert data["avg_rating"] == 10.0
    assert data["total_hours"] == 15.0