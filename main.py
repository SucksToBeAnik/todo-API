from fastapi import FastAPI
from Router import todo, auth

app = FastAPI()

app.include_router(todo.router)
app.include_router(auth.router)