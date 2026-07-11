from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status
from fastapi.params import Body
from random import randrange
app = FastAPI()


class Task(BaseModel):
    title: str
    description: str
    status: str


tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI",
        "description": "Finish CRUD lesson",
        "status": "Pending"
    },
    {
        "id": 2,
        "title": "Build API",
        "description": "Finish API lesson",
        "status": "In Progress"
    }
]


def find_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/tasks")
def get_tasks():
    return {"tasks": tasks}


@app.get("/tasks/{id}")
def get_task(id: int):
    task = find_task(id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {id} does not exist."
        )
    return task


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(body: Task):
    body_dict = body.model_dump()
    body_dict["id"] = randrange(1, 500)
    tasks.append(body_dict)
    return {"new_task": body_dict}


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):
    task = find_task(id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {id} does not exist."
        )
    tasks.remove(task)


@app.put("/tasks/{id}")
def update_task(id: int, body: Task):
    body_dict = body.model_dump()
    task = find_task(id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {id} does not exist."
        )
    body_dict["id"] = id
    task.update(body_dict)
    return task
