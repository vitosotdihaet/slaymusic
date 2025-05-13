from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, api_key
from sqlalchemy.orm import Session
from db.database import get_db_connection, SessionLocal
from models.users import User, Admin
from api.auth import get_hashed_password
import os
from dotenv import load_dotenv

def create_admin(username: str, password: str):
    db = SessionLocal()
    try:
        if (db.query(User).filter(User.name == username).first()):
            print("Admin already exists")
            return

        hash_password = get_hashed_password(password)

        user = User(name=username, password=hash_password)
        db.add(user)
        db.commit()

        admin = Admin(user_id=user.id)
        db.add(admin)
        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    
    finally:
        db.close()


security = HTTPBasic()
load_dotenv()

def verify_secret_key(credentials: HTTPBasicCredentials = Depends(security)):
    key = os.getenv("ADMIN_SECRET_KEY")
    
    if not key:
        raise HTTPException(status_code=500, detail="Secret key doesn't exist")

    print(credentials.username, credentials.password, key)
    if (credentials.username != "bootstrap" or credentials.password != key):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return True

router = APIRouter()

@router.post("/bootstrap-admin")
async def bootstrap_admin(username: str, password: str, auth: bool = Depends(verify_secret_key), db: Session = Depends(get_db_connection)):
    if (db.query(Admin).first()):
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    create_admin(username, password)

    return {"status": "success", "message" : "Admin has been created"}