import json
import pytest

from fastapi import HTTPException
from unittest.mock import MagicMock, patch

from src.db.models import Hero
from sqlalchemy.sql import operators
from src.app.routers import create_hero, get_heroes

# for post -> /hero


@pytest.mark.asyncio
async def test_create_hero_success(mock_db, hero_data):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "success",
        "results": [
            {
                "name": "Superman",
                "powerstats": {
                    "intelligence": "100",
                    "strength": "100",
                    "speed": "100",
                    "power": "100",
                },
                "biography": {
                    "full-name": "Clark Kent",
                    "publisher": "DC Comics",
                    "alignment": "good",
                },
                "image": {"url": "http://example.com/superman.jpg"},
            }
        ],
    }

    with patch("src.app.routers._call_api_method", return_value=mock_response):
        result = await create_hero(hero_data, mock_db)

        assert result["message"] == "Hero successfully added"
        assert result["hero"].name == "Superman"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_hero_empty_results(mock_db, hero_data):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "success", "results": []}

    with patch(
        "src.app.routers._call_api_method", return_value=mock_response
    ), pytest.raises(HTTPException) as exc_info:
        await create_hero(hero_data, mock_db)

    assert exc_info.value.status_code == 404
    assert "No results found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_hero_no_exact_match(mock_db, hero_data):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "success",
        "results": [
            {
                "name": "lol-kek",
            }
        ],
    }

    with patch(
        "src.app.routers._call_api_method", return_value=mock_response
    ), pytest.raises(HTTPException) as exc_info:
        await create_hero(hero_data, mock_db)

    assert exc_info.value.status_code == 404
    assert "No exact match found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_hero_duplicate(mock_db, hero_data):
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await create_hero(hero_data, mock_db)

    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail


# for get -> /hero/


@pytest.mark.asyncio
async def test_get_heroes_by_stats(db):
    mock_hero = MagicMock()
    db.query.return_value.filter.return_value.filter.return_value.filter.return_value.filter.return_value.all.return_value = [
        mock_hero
    ]

    filters = json.dumps(
        {
            "intelligence": {"eq": 90.0},
            "strength": {"eq": 85.5},
            "speed": {"eq": 70.0},
            "power": {"eq": 80.0},
        }
    )

    result = await get_heroes(filters=filters, db=db)

    assert result == [mock_hero]
    assert db.query.return_value.filter.call_count == 4


@pytest.mark.asyncio
async def test_get_heroes_by_name_and_stat(db):
    test_name = "Iron Man"
    mock_hero = MagicMock()
    db.query.return_value.filter.return_value.filter.return_value.all.return_value = [
        mock_hero
    ]

    filters = json.dumps({"intelligence": {"gte": 90.0}})
    result = await get_heroes(name=test_name, filters=filters, db=db)

    assert result == [mock_hero]
    db.query.assert_called_once_with(Hero)
    assert db.query.return_value.filter.call_count == 2

    first_filter_args, _ = db.query.return_value.filter.call_args_list[0]
    assert str(first_filter_args[0].left).lower() == "lower(heroes.name)"

    second_filter_args, _ = db.query.return_value.filter.call_args_list[1]
    assert str(second_filter_args[0].left) == "heroes.intelligence"
    assert second_filter_args[0].operator == operators.ge
