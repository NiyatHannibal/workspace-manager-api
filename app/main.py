from fastapi import FastAPI
from .routers import workspace, task, user, auth, membership
app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(workspace.router)
app.include_router(membership.router)
app.include_router(task.router)
