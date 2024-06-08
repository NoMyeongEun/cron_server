from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from .. import models
from ..database import engine, SessionLocal
from .auth import get_current_user, get_user_exception

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

class Task(BaseModel):
    title: str
    description: Optional[str]
    priority: int
    complete: bool

@router.get("/")
async def read_all(db: Session = Depends(get_db)): #user : dict = Depends(get_current_user)
    #if user is None:
        #raise get_user_exception()
    todo_model = db.query(models.Routines).\
        filter(models.Routines.owner_id == 1).all() # user.get("id")
    return todo_model

@router.post("/add-routine")
async def create_routine(routine: Routine, db: Session = Depends(get_db)):
    routine_model = models.Routines()
    routine_model.title = routine.title
    routine_model.description = routine.description
    routine_model.priority = routine.priority
    routine_model.complete = routine.complete
    routine_model.owner_id = 1 #dummy data -> 이후에는 현재 사용자 ID 값

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

@router.get("/{routine_id}/get-task/all")
async def get_all_tasks(r_id : int, db: Session = Depends(get_db)) :
    task_model = db.query(models.Tasks).\
        filter(models.Tasks.routine_id == r_id).all()
    return task_model

@router.post("/{routine_id}/add-task")
async def add_task(r_id : int, task : Task, db: Session = Depends(get_db)) :
    task_model = models.Tasks()
    task_model.title = task.title
    task_model.description = task.description
    task_model.priority = task.priority
    task_model.complete = False
    task_model.routine_id = r_id

    db.add(task_model)
    db.commit()

@router.get("/{routine_id}/{task_id}")
async def get_task(r_id : int, task_id : int, db: Session = Depends(get_db)) :
    task_model = db.query(models.Tasks).filter(models.Tasks.routine_id == r_id).filter(models.Tasks.id == task_id).first()
    return task_model

@router.post("/{routine_id}/edit-task/{task_id}")
async def edit_task(r_id : int, task_id :int, task : Task, db: Session = Depends(get_db)) :
    task_model = db.query(models.Tasks).filter(models.Tasks.routine_id == r_id).filter(models.Tasks.id == task_id).first()
    task_model.title = task.title
    task_model.description = task.description
    task_model.priority = task.priority

    db.add(task_model)
    db.commit()

@router.post("/{routine_id}/delete-task/{task_id}")
async def delete_task(r_id : int, task_id : int, db: Session = Depends(get_db)) :
    db.query(models.Tasks).filter(models.Tasks.routine_id == r_id).filter(models.Tasks.id == task_id).delete()
    db.commit()