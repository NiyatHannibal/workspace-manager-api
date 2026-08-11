from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/workspaces/{workspace_id}/members",
    tags=["Members"]
)


def verify_workspace_member(
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

    membership = db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == workspace_id,
        models.WorkspaceMember.user_id == current_user.id
    ).first()

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You are not a member of this workspace."
        )

    return workspace


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


@router.get("/", response_model=list[schemas.WorkspaceMemberResponse])
def get_members(
        workspace_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(oauth2.get_current_user)):
    verify_workspace_member(workspace_id, db, current_user)
    members = db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == workspace_id).all()
    return members


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.WorkspaceMemberResponse)
def create_member(
        body: schemas.WorkspaceMemberCreate,
        workspace_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(oauth2.get_current_user)):

    verify_workspace_owner(workspace_id, db, current_user)
    user = db.query(models.User).filter(
        models.User.id == body.user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {body.user_id} does not exist."
        )

    # Check if user is already a member of this workspace
    existing_member = db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == workspace_id,
        models.WorkspaceMember.user_id == body.user_id
    ).first()

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this workspace."
        )

    member = models.WorkspaceMember(
        workspace_id=workspace_id,
        user_id=body.user_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member
