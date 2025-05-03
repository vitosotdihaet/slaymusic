from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from db.database import get_db_connection
from models.users import User
from api.auth import create_access_token, verify_token, verify_password, get_hashed_password

router = APIRouter()

@router.get("/user{user_id}")
def get_users(user_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, created_at, updated_at FROM users WHERE id = %s", (user_id, ) )
            user = cur.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        print(f"{e}")
    finally:
        return {"id": user["id"], "name": user["name"], "created_at" : user["created_at"], "updated_at" : user["updated_at"]}
        # return User(**user)

@router.post("/register")
def register(user: User):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            hash_password = get_hashed_password(user.password)

            cur.execute("INSERT INTO users (name, password) VALUES (%s, %s) RETURNING id, name",
                        (user.name, hash_password))
            user = cur.fetchone()
            conn.commit()

            # access_token = create_access_token(data = {"sub" : str(user["id"])})
            # return {"access_token" : access_token}
            response = RedirectResponse(url="/login", status_code=303)
            return response
    except Exception as e:
        print(f"{e}")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, password FROM users WHERE name = %s", (form_data))
            user_db = cur.fetchone()
            if not user_db:
                raise HTTPException(status_code=404, detail="User not found")
            
            if (verify_password(get_hashed_password(form_data.password), user_db["password"])):
                raise HTTPException(status_code=401, detail="Wrong login or password")
            
            access_token = create_access_token(data = {"sub" : str(user_db["id"])})
            response = RedirectResponse(url="/", status_code=303)
            response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
            return response

    except Exception as e:
        print(f"{e}")
        raise HTTPException(
            status_code=500,
            detail="Login failed")


