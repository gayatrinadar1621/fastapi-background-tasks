from fastapi import FastAPI
from src.auth.routes import user_router

app = FastAPI()
app.include_router(user_router)

