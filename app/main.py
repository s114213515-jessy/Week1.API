from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.api.notes import router as notes_router

STUDENT_PREFIX = "/s114213515"
PUBLIC_DIRECTORY = Path(__file__).resolve().parent.parent / "public"


class HtmlCssOnlyStaticFiles(StaticFiles):
    allowed_extensions = {".css", ".html", ".svg"}
    allowed_directories = {"js", "json"}

    async def get_response(self, path: str, scope: dict[str, Any]) -> Response:
        requested_path = Path(path)
        is_allowed_file = requested_path.suffix.lower() in self.allowed_extensions
        is_allowed_directory = bool(requested_path.parts) and (
            requested_path.parts[0] in self.allowed_directories
        )

        if path.strip("/") and not (is_allowed_file or is_allowed_directory):
            raise HTTPException(status_code=404, detail="Public file not found")

        return await super().get_response(path, scope)


app = FastAPI(title="My Backend API")
app.include_router(notes_router, prefix="/api")


@app.middleware("http")
async def support_student_subpath(request: Request, call_next):
    path = request.scope["path"]
    if path == STUDENT_PREFIX or path.startswith(f"{STUDENT_PREFIX}/"):
        normalized_path = path[len(STUDENT_PREFIX) :] or "/"
        request.scope["path"] = normalized_path
        request.scope["raw_path"] = normalized_path.encode("utf-8")

    return await call_next(request)


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


app.mount(
    "/",
    HtmlCssOnlyStaticFiles(directory=PUBLIC_DIRECTORY, html=True),
    name="public",
)
