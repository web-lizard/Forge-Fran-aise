from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import audio, bootstrap, codex, course, health, lessons, practice, profiles, progress, sections, settings, vulgar

app = FastAPI(
    title="Forge Française API",
    description="Imperial French learning engine",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5197",
        "http://localhost:5197",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(bootstrap.router, prefix="/api")
app.include_router(course.router, prefix="/api")
app.include_router(sections.router, prefix="/api")
app.include_router(lessons.router, prefix="/api")
app.include_router(practice.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(profiles.router, prefix="/api")
app.include_router(audio.router, prefix="/api")
app.include_router(codex.router, prefix="/api")
app.include_router(vulgar.router, prefix="/api")
