from pydantic import BaseModel


class HeroCreate(BaseModel):
    name: str
