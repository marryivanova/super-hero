import pytest

from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.helpers.models import HeroCreate


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    return db


@pytest.fixture
def hero_data():
    return HeroCreate(name="Superman")


@pytest.fixture
def db():
    db = MagicMock(spec=Session)
    db.query.return_value.filter.return_value = db.query.return_value
    db.query.return_value.all.return_value = []
    return db
