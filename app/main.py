import json
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from fastapi import FastAPI, status

from app.database import get_connection, init_db
from app.schemas import PlantCreate, PlantResponse

TEMPLATES_FILE = Path(__file__).resolve().parent / "plant_templates.json"


def load_plant_templates() -> list[dict]:
    with open(TEMPLATES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Plantagotchi", version="0.1.0", lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Plantagotchi API functioneaza!"}


@app.get("/templates")
def get_plant_templates():
    return load_plant_templates()


@app.post("/plants", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
def create_plant(plant: PlantCreate):
    last_watered = plant.last_watered or date.today().isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO plants (user_id, name, species, watering_frequency_days, light_requirement, last_watered)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                plant.name,
                plant.species,
                plant.watering_frequency_days,
                plant.light_requirement,
                last_watered,
            ),
        )
        plant_id = cursor.lastrowid
        conn.commit()

        row = cursor.execute(
            "SELECT * FROM plants WHERE id = ?", (plant_id,)
        ).fetchone()

    return dict(row)


@app.get("/plants", response_model=list[PlantResponse])
def list_plants():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM plants WHERE is_alive = 1 ORDER BY id DESC"
        ).fetchall()

    return [dict(row) for row in rows]