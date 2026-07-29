from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=list[schemas.UserResponse])
def get_user(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    print(current_user.password)
    users = db.query(models.User).all()
    return users


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(body: schemas.User, db: Session = Depends(get_db)):
    body.password = utils.hash_password(body.password)
    user = models.User(**body.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    print(current_user)
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {id} does not exist.")
    return user
