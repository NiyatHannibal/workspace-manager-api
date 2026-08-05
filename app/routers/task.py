from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/workspaces/{workspace_id}/tasks",
    tags=["Tasks"]
)


def verify_workspace_owner(
    workspace_id: int,
    db: Session,
    current_user: models.User
):
    workspace = db.query(models.Workspace).filter(
        models.Workspace.id == workspace_id
    ).first()

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} does not exist."
        )

    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this workspace."
        )

    return workspace


@router.get("/", response_model=list[schemas.TaskResponse])
def get_tasks(
        workspace_id: int,
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        limit: int = 10,
        skip: int = 0,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(oauth2.get_current_user)):

    workspace = verify_workspace_owner(workspace_id, db, current_user)

    query = db.query(models.Task)
    query = query.filter(
        models.Task.workspace_id == workspace_id)
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


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(workspace_id: int, task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    workspace = verify_workspace_owner(workspace_id, db, current_user)

    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.workspace_id == workspace_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"task with ID {task_id} does not exist."
        )
    return task


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TaskResponse)
def create_task(workspace_id: int, body: schemas.TaskBase, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    workspace = verify_workspace_owner(workspace_id, db, current_user)

    task = models.Task(**body.model_dump(), workspace_id=workspace_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(workspace_id: int, task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    workspace = verify_workspace_owner(workspace_id, db, current_user)

    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.workspace_id == workspace_id
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"task with ID {task_id} does not exist."
        )
    db.delete(task)
    db.commit()


@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(workspace_id: int, task_id: int, body: schemas.TaskBase, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    workspace = verify_workspace_owner(workspace_id, db, current_user)

    task_query = db.query(models.Task).filter(models.Task.id == task_id,
                                              models.Task.workspace_id == workspace_id)

    if task_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"task with ID {task_id} does not exist."
        )
    task_query.update(body.model_dump(), synchronize_session=False)
    db.commit()
    return task_query.first()
