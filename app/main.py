from fastapi import FastAPI
from pydantic import BaseModel
from app.api.notes import router as notes_router

app = FastAPI(title="My Backend API")
app.include_router(notes_router)


class Item(BaseModel):
    name: str
    price: float


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": "0.1.0"}


@app.post("/items")
def create_item(item: Item):
    return item