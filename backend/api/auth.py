from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRED_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")
def create_access_token(data: dict):
    print(SECRET_KEY, ALGORITHM)
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRED_MINUTES)
    to_encode.update({"exp" : expire})
    return jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_password(entered_password: str, hashed_password: str):
    return pwd_context.verify(entered_password, hashed_password)

def get_hashed_password(entered_password: str):
    return pwd_context.hash(entered_password)
