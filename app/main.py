from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.api.notes import router as notes_router

PUBLIC_DIRECTORY = Path(__file__).resolve().parent.parent / "public"
PUBLIC_FILES = {
    "index.html": "index.html",
    "styles.css": "styles.css",
}

app = FastAPI(title="My Backend API")
app.include_router(notes_router, prefix="/api")


class Item(BaseModel):
    name: str
    price: float


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/version")
def version():
    return {"version": "0.1.0"}


@app.post("/api/items")
def create_item(item: Item):
    return item


@app.get("/", include_in_schema=False)
def serve_homepage():
    return FileResponse(PUBLIC_DIRECTORY / "index.html")


@app.get("/{file_path:path}", include_in_schema=False)
def serve_public_file(file_path: str):
    file_name = PUBLIC_FILES.get(file_path)
    if file_name is None:
        raise HTTPException(status_code=404, detail="Public file not found")

    return FileResponse(PUBLIC_DIRECTORY / file_name)
