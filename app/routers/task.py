from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.get("/", response_model=list[schemas.TaskResponse])
def get_tasks(
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        limit: int = 10,
        skip: int = 0,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(oauth2.get_current_user)):

    query = db.query(models.Task)
    query = query.filter(
        models.Task.owner_id == current_user.id)
    if search:
        query = query.filter(
            models.Task.title.ilike(f"%{search}%"))
    if status:
        query = query.filter(
            models.Task.status == status)
    if priority:
        query = query.filter(
            models.Task.priority == priority)

    query = query.offset(skip).limit(limit)
    tasks = query.all()
    return tasks


@router.get("/{id}", response_model=schemas.TaskResponse)
def get_task(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    task = db.query(models.Task).filter(
        models.Task.id == id,
        models.Task.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {id} does not exist."
        )
    return task


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TaskResponse)
def create_task(body: schemas.TaskBase, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    task = models.Task(**body.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    task = db.query(models.Task).filter(
        models.Task.id == id,
        models.Task.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {id} does not exist."
        )
    db.delete(task)
    db.commit()


@router.put("/{id}", response_model=schemas.TaskResponse)
def update_task(id: int, body: schemas.TaskBase, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    task_query = db.query(models.Task).filter(models.Task.id == id,
                                              models.Task.owner_id == current_user.id)
    if task_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {id} does not exist."
        )
    task_query.update(body.model_dump(), synchronize_session=False)
    db.commit()
    return task_query.first()
