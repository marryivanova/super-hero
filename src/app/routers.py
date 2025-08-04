import json
import typing as t
from fastapi import Request
from sqlalchemy import func

from sqlalchemy.orm import Session
from fastapi import APIRouter, Query, HTTPException, Depends


from src.db.models import Hero
from src.db.data_base import get_db
from src.helpers.models import HeroCreate
from src.helpers.static_content import templates
from src.utils.custom_logger import get_logger
from src.app._helpers import apply_json_filters, _call_api_method, Endpoint

logger = get_logger(__name__)
logger.propagate = False

router = APIRouter(tags=["Super hero"])


@router.get("/", include_in_schema=False)
async def serve_ui(request: Request):
    logger.info("Serving UI template")
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/hero")
async def create_hero(hero_data: HeroCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating new hero with name: {hero_data.name}")
    name = hero_data.name

    existing_hero = (
        db.query(Hero).filter(func.lower(Hero.name) == func.lower(name)).first()
    )
    if existing_hero:
        error_msg = f"Hero with name '{name}' already exists in database"
        logger.warning(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    logger.debug(f"Searching for hero '{name}' in external API")
    response = _call_api_method(endpoint=Endpoint.SEARCH, search_name=name)

    if response.status_code != 200 or response.json().get("response") == "error":
        error_msg = f"Hero '{name}' not found in superheroapi.com"
        logger.warning(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)

    data = response.json()
    logger.debug(f"API response data: {data}")

    if not data.get("results"):
        error_msg = f"No results found for hero '{name}'"
        logger.warning(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)

    character = None
    for result in data["results"]:
        if result["name"].lower() == name.lower():
            character = result
            break

    if not character:
        error_msg = f"No exact match found for hero '{name}' in API results"
        logger.warning(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)

    logger.debug(f"Found matching character: {character['name']}")

    def safe_float(value, default=0.0):
        """Safely convert value to float, handling 'null' string and None cases."""
        if value is None or str(value).lower() == "null":
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    try:
        powerstats = character.get("powerstats", {})
        biography = character.get("biography", {})
        image = character.get("image", {})

        new_hero = Hero(
            name=character.get("name", "").strip(),
            intelligence=safe_float(powerstats.get("intelligence")),
            strength=safe_float(powerstats.get("strength")),
            speed=safe_float(powerstats.get("speed")),
            power=safe_float(powerstats.get("power")),
            full_name=biography.get("full-name", "").strip(),
            publisher=biography.get("publisher", "").strip(),
            alignment=biography.get("alignment", "").strip(),
            image_url=image.get("url", "").strip(),
        )

        db.add(new_hero)
        db.commit()
        db.refresh(new_hero)
        logger.info(f"Successfully created new hero with ID: {new_hero.id}")

        return {"message": "Hero successfully added", "hero": new_hero}

    except Exception as e:
        db.rollback()
        error_msg = f"Error creating hero: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/hero/")
async def get_heroes(
    name: t.Optional[str] = None,
    intelligence_eq: t.Optional[float] = None,
    intelligence_gte: t.Optional[float] = None,
    intelligence_lte: t.Optional[float] = None,
    filters: t.Optional[str] = Query(
        None,
        description="Advanced filters in JSON format. Example: "
        '{"power": {"gte": 90}, "speed": {"lte": 50}}',
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve heroes with optional filtering capabilities.

    Parameters:
    - **name**: Exact match for hero name (case-insensitive)
    - **intelligence_eq**: Intelligence exact match
    - **intelligence_gte**: Intelligence greater than or equal
    - **intelligence_lte**: Intelligence less than or equal
    - **filters**: Advanced JSON filters for complex conditions

    Examples:
    - Basic: `/hero/?intelligence_gte=90&speed_lte=50`
    - Advanced: `/hero/?filters={"power": {"gte": 90}, "speed": {"lte": 50}}`

    Returns:
    - List of Hero objects matching the criteria
    - 404 if no heroes found
    - 400 for invalid JSON filters
    """
    query = db.query(Hero)

    if name:
        query = query.filter(func.lower(Hero.name) == func.lower(name))

    if intelligence_eq is not None:
        query = query.filter(Hero.intelligence == intelligence_eq)
    if intelligence_gte is not None:
        query = query.filter(Hero.intelligence >= intelligence_gte)
    if intelligence_lte is not None:
        query = query.filter(Hero.intelligence <= intelligence_lte)

    if filters:
        try:
            filters_data = json.loads(filters)
            query = apply_json_filters(query, filters_data)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid JSON filters format: {str(e)}"
            )

    heroes = query.all()
    if not heroes:
        raise HTTPException(
            status_code=404, detail="No heroes found matching the specified criteria"
        )
    return heroes
