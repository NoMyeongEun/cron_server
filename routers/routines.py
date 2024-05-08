from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/routines",
    tags=['routines'],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Routine(BaseModel):
    title: str
    description: Optional[str]
    priority: int
    complete: bool

@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Routines).all()

@router.post("/add-routine")
async def create_routine(routine: Routine, db: Session = Depends(get_db)):
    routine_model = models.Routines()
    routine_model.title = routine.title
    routine_model.description = routine.description
    routine_model.priority = routine.priority
    routine_model.complete = routine.complete
    
    db.add(routine_model)
    db.commit()
    
@router.post("/edit-routine/{routine_id}")
async def edit_routine(routine_id : int, title: str,
                           description, priority: int,
                         db: Session = Depends(get_db)) :
    routnie_model = db.query(models.Routines).filter(models.Routines.id == routine_id).first()

    routnie_model.title = title
    routnie_model.description = description
    routnie_model.priority = priority

    db.add(routnie_model)
    db.commit()


@router.post("/delete-routine/{routine_id}")
async def delete_routine(routine_id : int, db: Session = Depends(get_db)) :
    db.query(models.Routines).filter(models.Routines.id == routine_id).delete()
    db.commit()
