import json
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI

from app.database import init_db

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