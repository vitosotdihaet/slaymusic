from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from depends import lifespan
from api.routers import music

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(music.router)
