from fastapi import FastAPI
from routes.users import users_router
from routes.admin import admin_router
from routes.forms import application_form_router
from dashboard.trainee import trainee_router
from dashboard.agent import agent_router

import cloudinary
import os

cloudinary.config(
    cloud_name = os.getenv("CLOUD_NAME"),
    api_key = os.getenv("API_KEY"),
    api_secret = os.getenv("API_SECRET"),
    )

app = FastAPI(title="A Career Grooming Agency Platform API")

@app.get("/")
def get_home():
    return {
        "status": "ok",
        "message": "Welcome to Career Grooming Agency"
    }

app.include_router(users_router)
app.include_router(admin_router)
app.include_router(application_form_router)
app.include_router(trainee_router)
app.include_router(agent_router)