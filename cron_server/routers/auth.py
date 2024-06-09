from fastapi import HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from jose import jwt, JWTError
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv

from .. import models
from ..database import engine, SessionLocal

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=['auth'],
    responses={404: {"description": "Not found"}}
)

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZGluZyIsImlkIjoxLCJleHAiOjE3MTUyMTE2ODh9.UxR8YRMnWCaH4Gbfubeufv2wRCWD6x-77OD0D2B_VX4")

models.Base.metadata.create_all(bind=engine)

class CreateUser(BaseModel):
    email: str
    password: str
    username: str
    gender : str
    goal : List[str]
    
class CheckEmail(BaseModel):
    email: str

class CheckPwd(BaseModel):
    email: str
    pwd : str

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# user 인증 에러 함수
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"},
    )
    return credentials_exception

# token 인증 에러 함수
def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate":"Bearer"},
    )
    return token_exception_response

def get_password_hash(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(email: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.email == email).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise get_user_exception()
        return {"username": username, "id": user_id}
    except JWTError:
        return get_user_exception()


async def get_user_by_email(email: str, db):
    result = db.query(models.Users).filter(models.Users.email == email).first()
    return result

@router.post("/register")
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = models.Users()
    create_user_model.email = create_user.email
    
    hash_password = get_password_hash(create_user.password)
    create_user_model.hashed_password = hash_password
    
    create_user_model.username = create_user.username
    create_user_model.gender = create_user.gender
    create_user_model.goal = json.dumps(create_user.goal, ensure_ascii= False)

    db.add(create_user_model)
    db.commit()

@router.post("/check")
async def check_user(check : CheckEmail, db : Session = Depends(get_db)) :
    result = await get_user_by_email(check.email, db)
    if result is None :
        return {"registered" : "false"}
    else :
        return {"registered" : "true"}

@router.post("/verify")
async def login_for_registered_user(form_data: CheckPwd,
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.email, form_data.pwd, db)
    if not user:
        return {"result": "fail"}
    else :
        return {"result": "success", "username" : user.username, "gender" : user.gender, "goal" : user.goal}

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return token_exception()
    token_expires = timedelta(minutes=20)
    token = create_access_token(user.username,
                                user.id,
                                expires_delta=token_expires)
    return {"token": token}