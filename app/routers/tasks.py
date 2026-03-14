from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Task, User
from app.schemas import TaskCreate,TaskResponse,TaskUpdate
from app.dependencies import get_current_user,get_admin_user

router=APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post("/",response_model=TaskResponse,status_code=status.HTTP_201_CREATED)
def create_task(
    task:TaskCreate,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    new_task=Task(**task.model_dump(),owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/",response_model=List[TaskResponse])
def get_tasks(
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    if current_user.role=="admin":
        return db.query(Task).all()
    return db.query(Task).filter(Task.owner_id==current_user.id).all()

@router.get("/{task_id}",response_model=TaskResponse)
def get_task(
    task_id:int,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    task=db.query(Task).filter(Task.id==task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if current_user.id!=task.owner_id and current_user.role!="admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized to view the task"
        )
    return task

@router.put("/{task_id}",response_model=TaskResponse)
def update_task(
    task_id:int,
    task_update:TaskUpdate,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    task=db.query(Task).filter(Task.id==task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if current_user.id!=task.owner_id and current_user.role!="admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized to update the task"
        )
    update_data=task_update.model_dump(exclude_unset=True)
    for field,value in update_data.items():
        setattr(task,field,value)

    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id:int,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    task=db.query(Task).filter(Task.id==task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    if current_user.id!=task.owner_id and current_user.role!="admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized to delete the task"
        )
    db.delete(task)
    db.commit()
    return None