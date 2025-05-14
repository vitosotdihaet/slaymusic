from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configs.logging import logger
from configs.environment import settings
from configs.depends import lifespan

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("settings are: %s", settings)
