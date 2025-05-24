from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configs.depends import lifespan
from configs.logging import logger
from configs.environment import settings
from api.routers import album, artist, track, genre
from api.routers import user_activity
from api.routers import users
from api.routers import misc
from api.routers import track_queue


app = FastAPI(lifespan=lifespan)

logger.info("settings are: %s", settings)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_activity.router)
app.include_router(album.router)
app.include_router(artist.router)
app.include_router(track.router)
app.include_router(genre.router)
app.include_router(users.router)
app.include_router(misc.router)
app.include_router(track_queue.router)
