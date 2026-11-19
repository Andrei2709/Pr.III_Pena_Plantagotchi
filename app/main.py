from fastapi import FastAPI

app = FastAPI(title="Plantagotchi", version="0.1.0")


@app.get("/")
def read_root():
    return {"message": "Plantagotchi API functioneaza!"}