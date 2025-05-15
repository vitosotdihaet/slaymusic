from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configs.logging import logger
from configs.environment import settings
from configs.depends import lifespan
from api.routers import album, artist, track

from api.routers import user_activity


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

logger.info("settings are: %s", settings)

app.include_router(user_activity.router)
