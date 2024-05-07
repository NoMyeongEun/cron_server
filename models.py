from database import Base
from typing import Optional, List
from pydantic import BaseModel, Field

class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str

class Routine(BaseModel):
    title : str
    description : Optional[str]
    icon : str