from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from db.database import get_db_connection
from models.users import User, Admin
from schemas.users import UserCreate
from api.auth import create_access_token, verify_token, verify_password, get_hashed_password

router = APIRouter()

@router.get("/main")
def main():
    return "- Say my name.\n - I don't know\n - You do know. You all do know who I am\n"


@router.get("/user/{user_id}")
def get_users(user_id: int, db: Session = Depends(get_db_connection)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "created_at" : user.created_at, "updated_at" : user.updated_at}


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db_connection)):
    try:
        hash_password = get_hashed_password(user.password)
        new_user = User(name=user.name, password=hash_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        response = RedirectResponse(url="/api/main", status_code=303)
        return response
        
    except Exception as e:
        db.rollback()
        print(f"{e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_class=RedirectResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_connection)):

    user_db = db.query(User).filter(User.name == form_data.username).first()
    
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not (verify_password(form_data.password, user_db.password)):
        raise HTTPException(status_code=401, detail="Wrong password")
    
    is_admin = db.query(Admin).filter(Admin.user_id == user_db.id).first() is not None

    access_token = create_access_token(data = {"sub" : str(user_db.id), "is_admin" : is_admin}) 

    response = RedirectResponse(url=f"/api/user/{user_db.id}", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)

    return response
