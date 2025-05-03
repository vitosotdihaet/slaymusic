# import time
from fastapi import FastAPI
from api import users


app = FastAPI()
app.include_router(users.router, prefix="/api")

# if __name__ == "__main__":
#     
#     # uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("BACKEND_PORT", "8000"), reload=True)


# # while True:
# #     print(f'hi {time.time()}')
# #     time.sleep(5)
