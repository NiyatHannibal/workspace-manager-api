from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy import select, func
router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"]
)


# @router.get("/", response_model=list[schemas.WorkspaceResponse])
# def get_workspaces(
#         search: str | None = None,
#         limit: int = 10,
#         skip: int = 0,
#         db: Session = Depends(get_db),
#         current_user: models.User = Depends(oauth2.get_current_user)):

#     query = db.query(models.Workspace)
#     query = query.filter(
#         models.Workspace.owner_id == current_user.id)
#     if search:
#         query = query.filter(
#             models.Workspace.name.ilike(f"%{search}%"))

#     query = query.offset(skip).limit(limit)
#     workspaces = query.all()
#     return workspaces


# @router.get("/{id}", response_model=schemas.WorkspaceResponse)
# def get_workspace(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
#     workspace = db.query(models.Workspace).filter(
#         models.Workspace.id == id,
#         models.Workspace.owner_id == current_user.id
#     ).first()

#     if not workspace:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Item with ID {id} does not exist."
#         )
#     return workspace


# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.WorkspaceResponse)
# def create_workspace(body: schemas.WorkspaceBase, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
#     workspace = models.Workspace(**body.model_dump(), owner_id=current_user.id)
#     db.add(workspace)
#     db.flush()
#     membership = models.WorkspaceMember(
#         workspace_id=workspace.id, user_id=current_user.id)
#     db.add(membership)
#     db.commit()
#     db.refresh(workspace)
#     return workspace


# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_task(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
#     workspace = db.query(models.Workspace).filter(
#         models.Workspace.id == id,
#         models.Workspace.owner_id == current_user.id
#     ).first()
#     if not workspace:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Item with ID {id} does not exist."
#         )
#     db.delete(workspace)
#     db.commit()


# @router.put("/{id}", response_model=schemas.WorkspaceResponse)
# def update_workspace(id: int, body: schemas.WorkspaceBase, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
#     workspace_query = db.query(models.Workspace).filter(models.Workspace.id == id,
#                                                         models.Workspace.owner_id == current_user.id)
#     if workspace_query.first() is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Item with ID {id} does not exist."
#         )
#     workspace_query.update(body.model_dump(), synchronize_session=False)
#     db.commit()
#     return workspace_query.first()


# exercise
@router.get('/owners', response_model=list[tuple[schemas.WorkspaceResponse, schemas.UserResponse]])
def get_workspace_with_owners(db: Session = Depends(get_db)):
    stmt = (
        select(models.Workspace, models.User)
        .join(models.User, models.Workspace.owner_id == models.User.id)
    )

    results = db.execute(stmt).all()

    return results


@router.get('/owner/{workspace_id}', response_model=tuple[schemas.WorkspaceResponse, schemas.UserResponse])
def get_owner(workspace_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(models.Workspace, models.User)
        .join(models.User, models.Workspace.owner_id == models.User.id)
        .where(models.Workspace.id == workspace_id)
    )

    result = db.execute(stmt).first()

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"workspace with {workspace_id} not found"
        )

    return result


@router.get('/owner/{workspace_id}/members', response_model=list[schemas.UserResponse])
def get_members(workspace_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(models.User)
        .join(models.WorkspaceMember, models.User.id == models.WorkspaceMember.user_id)
        .where(models.WorkspaceMember.workspace_id == workspace_id)
    )

    users = db.execute(stmt).scalars().all()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"workspace with {workspace_id} not found"
        )

    return users


@router.get('/member-count')
def get_members(db: Session = Depends(get_db)):
    stmt = (
        select(
            models.Workspace.id,
            models.Workspace.name,
            func.count(models.WorkspaceMember.id).label("members_count"))

        .outerjoin(models.WorkspaceMember,
                   models.Workspace.id == models.WorkspaceMember.workspace_id)
        .group_by(models.Workspace.id, models.Workspace.name)
        .having(func.count(models.WorkspaceMember.id) == 1)
    )

    results = db.execute(stmt).mappings().all()

    return results
