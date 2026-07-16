from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db
app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/tasks", response_model=list[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks


@app.get("/tasks/{id}", response_model=schemas.TaskResponse)
def get_task(id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {id} does not exist."
        )
    return task


@app.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=schemas.TaskResponse)
def create_task(body: schemas.TaskBase, db: Session = Depends(get_db)):
    task = models.Task(**body.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {id} does not exist."
        )
    db.delete(task)
    db.commit()


@app.put("/tasks/{id}", response_model=schemas.TaskResponse)
def update_task(id: int, body: schemas.TaskBase, db: Session = Depends(get_db)):
    task_query = db.query(models.Task).filter(models.Task.id == id)
    if task_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {id} does not exist."
        )
    task_query.update(body.model_dump(), synchronize_session=False)
    db.commit()
    return task_query.first()
