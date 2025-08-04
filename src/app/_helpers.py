import requests
import typing as t
from enum import Enum, auto


from src.db.models import Hero
from src.config.settings import settings
from src.utils.custom_logger import get_logger


logger = get_logger(__name__)
logger.propagate = False


class Endpoint(Enum):
    """Available API endpoints for Superhero API."""

    POWERSTATS = auto()
    BIOGRAPHY = auto()
    APPEARANCE = auto()
    WORK = auto()
    CONNECTIONS = auto()
    IMAGE = auto()
    SEARCH = auto()
    ID = auto()

    @property
    def path(self) -> str:
        """Returns the string representation for API URL."""
        return self.name.lower()


def _call_api_method(
    endpoint: t.Union[Endpoint, str],
    hero_id: t.Union[int, None] = None,
    search_name: t.Union[str, None] = None,
) -> requests.Response:
    """
    Universal method for working with the Superhero API.

    Args:
        endpoint: One of the predefined Endpoint enum values
        hero_id: Hero ID (required for most endpoints)
        search_name: Name for search (required for SEARCH endpoint)

    Returns:
        API response

    Raises:
        ValueError: If required parameters are missing
    """
    logger.info(
        f"Calling API method. Endpoint: {endpoint}, hero_id: {hero_id}, search_name: {search_name}"
    )

    base_url = f"{settings.API_HERO}/{settings.TOKEN}"

    if isinstance(endpoint, str):
        try:
            endpoint = Endpoint[endpoint.upper()]
            logger.debug(f"Converted string endpoint to Enum: {endpoint}")
        except KeyError:
            error_msg = f"Unknown endpoint: {endpoint}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    if endpoint == Endpoint.SEARCH:
        if not search_name:
            error_msg = "search_name must be provided for search"
            logger.error(error_msg)
            raise ValueError(error_msg)
        url = f"{base_url}/search/{search_name}"
    elif endpoint in [
        Endpoint.POWERSTATS,
        Endpoint.BIOGRAPHY,
        Endpoint.APPEARANCE,
        Endpoint.WORK,
        Endpoint.CONNECTIONS,
        Endpoint.IMAGE,
    ]:
        if not hero_id:
            error_msg = "hero_id must be provided for this endpoint"
            logger.error(error_msg)
            raise ValueError(error_msg)
        url = f"{base_url}/{hero_id}/{endpoint.path}"
    elif endpoint == Endpoint.ID:
        if not hero_id:
            error_msg = "hero_id must be provided when fetching by ID"
            logger.error(error_msg)
            raise ValueError(error_msg)
        url = f"{base_url}/{hero_id}"
    else:
        error_msg = f"Unsupported endpoint: {endpoint}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.debug(f"Constructed API URL: {url}")
    response = requests.get(url)
    logger.debug(f"API response status: {response.status_code}")

    return response


def apply_json_filters(query, filters):
    """
    Applies JSON-based filters to SQLAlchemy query.

    Supported operators:
    - eq: Equal to
    - gte: Greater than or equal
    - lte: Less than or equal

    Example input:
    {
        "power": {"gte": 90},
        "speed": {"lte": 50}
    }
    """
    for field, conditions in filters.items():
        column = getattr(Hero, field, None)
        if not column:
            continue
        for op, value in conditions.items():
            if op == "eq":
                query = query.filter(column == value)
            elif op == "gte":
                query = query.filter(column >= value)
            elif op == "lte":
                query = query.filter(column <= value)
    return query
