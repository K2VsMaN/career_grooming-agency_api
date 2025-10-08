from fastapi import FastAPI
from routes.users import users_router

app = FastAPI(title="A Career Grooming Agency Platform API")

@app.get("/")
def get_home():
    return {
        "status": "ok",
        "message": "Welcome to Career Grooming Agency"
    }

app.include_router(users_router)