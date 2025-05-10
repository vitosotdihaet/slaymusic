from fastapi import FastAPI
from api import users, admin


app = FastAPI()
app.include_router(users.router, prefix="/api")
app.include_router(admin.router)
