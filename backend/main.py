from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configs.depends import lifespan
from api.routers import album, artist, track
from api import users, admin

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(album.router)
app.include_router(artist.router)
app.include_router(track.router)

app.include_router(users.router, prefix="/api")
app.include_router(admin.router)
