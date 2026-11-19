from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Plantagotchi", version="0.1.0", lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Plantagotchi API functioneaza!"}