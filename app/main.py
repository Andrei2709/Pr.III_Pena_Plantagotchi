import json
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import get_connection, init_db
from app.schemas import PlantCreate, PlantResponse

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_FILE = Path(__file__).resolve().parent / "plant_templates.json"


def load_plant_templates() -> list[dict]:
    with open(TEMPLATES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Plantagotchi", version="0.1.0", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    with get_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = 1").fetchone()
        plants = conn.execute(
            "SELECT * FROM plants WHERE is_alive = 1 ORDER BY id DESC"
        ).fetchall()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": dict(user),
            "plants": [dict(row) for row in plants],
        },
    )


@app.get("/add", response_class=HTMLResponse)
def add_plant_page(request: Request):
    with get_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = 1").fetchone()

    return templates.TemplateResponse(
        request=request,
        name="add_plant.html",
        context={
            "user": dict(user),
            "plant_templates": load_plant_templates(),
            "today": date.today().isoformat(),
        },
    )


@app.post("/add")
def add_plant_form(
    name: str = Form(...),
    species: str = Form(...),
    watering_frequency_days: int = Form(...),
    light_requirement: str = Form(...),
    last_watered: str = Form(...),
):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO plants (user_id, name, species, watering_frequency_days, light_requirement, last_watered)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                name.strip(),
                species.strip(),
                watering_frequency_days,
                light_requirement,
                last_watered,
            ),
        )
        conn.commit()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Plantagotchi"}


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