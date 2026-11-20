from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class PlantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Spike"])
    species: str = Field(..., min_length=1, max_length=100, examples=["Cactus"])
    watering_frequency_days: int = Field(..., gt=0, le=365, examples=[14])
    light_requirement: str = Field(default="Medie", examples=["Ridicata"])
    last_watered: Optional[str] = Field(
        default=None,
        description="Data ultimei udari in format YYYY-MM-DD (implicit azi)",
        examples=[date.today().isoformat()],
    )


class PlantResponse(BaseModel):
    id: int
    user_id: int
    name: str
    species: str
    watering_frequency_days: int
    light_requirement: str
    last_watered: str
    is_alive: bool