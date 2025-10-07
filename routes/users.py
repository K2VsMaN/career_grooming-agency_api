from fastapi import APIRouter, Form, Depends
from db import users_collection
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Annotated
from enum import Enum
import bcrypt, jwt, os
from datetime import datetime, timedelta, timezone
from bson import ObjectId

users_router = APIRouter(tags=["Users"])

class UserDetails(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserRole(str, Enum):
    AGENT = "agent"
    USER = "trainee"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

PASSCODE_REQUIRED = "CGA2025"

@users_router.post("/users/signup")
def register_user(
        username: Annotated[str, Form()],
        email: Annotated[EmailStr, Form()],
        password: Annotated[str, Form(min_length=8)],
        confirm_password: Annotated[str, Form()],
        role: Annotated[UserRole, Form()] = UserRole.USER):

    user_count = users_collection.count_documents({"email": email})
    if user_count > 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "User already exists!")

    if password != confirm_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Passwords do not match!")

    hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    user_created = {
        "username": username,
        "email": email,
        "password": hash_password,
        "role": role
    }

    registered_user = users_collection.insert_one(user_created)

    return {
        "message": "Signup successful",
        "user_id": str(registered_user.inserted_id)
    }

@users_router.post("/users/login")
def login_user(
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=8)],
    passcode: Annotated[str, Form]
):
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found!")

    correct_password = bcrypt.checkpw(password.encode(), user["password"])
    if not correct_password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong credentials!")

    if user["role"] == "trainee":
        if passcode != PASSCODE_REQUIRED:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Invalid or missing passcode!")


    encoded_jwt = jwt.encode({
            "id": str(user["_id"]),
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=60)
        }, os.getenv("JWT_SECRET_KEY"), os.getenv("JWT_ALGORITHM"))

    return {
        "message": "Login successful",
        "access_token": encoded_jwt,
        "role": user["role"]
    }


@users_router.post("/users/register/trainee")
def register_trainee(
    full_name: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    phone_number: Annotated[str, Form()],
    emergency_contact: Annotated[str, Form()],    
    date_of_birth: Annotated[str, Form()],
    address: Annotated[str, Form()],
    gender: Annotated[Gender, Form()] = Gender.MALE
):
    # Check if agent already exists
    if users_collection.find_one({"email": email}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Email already registered!")


    # Create agent document
    trainee = {
        "full_name": full_name,
        "email": email,
        "phone number": phone_number,
        "emergency contact": emergency_contact,
        "gender": gender,
        "date of birth": date_of_birth,
        "address": address,
        "role": "trainee"
    }

    users_collection.insert_one(trainee)
    return {"message": "Trainee registered successfully!"}


@users_router.post("/users/register/agent")
def register_agent(
    full_name: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    phone_number: Annotated[str, Form()],
    company: Annotated[str, Form()],
    years_of_experience: Annotated[str, Form()],    
    date_of_birth: Annotated[str, Form()],
    address: Annotated[str, Form()],
    gender: Annotated[Gender, Form()] = Gender.MALE
):
    # Check if agent already exists
    if users_collection.find_one({"email": email}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Email already registered!")

    # Create agent document
    agent = {
        "full_name": full_name,
        "email": email,
        "phone": phone_number,
        "company": company,
        "years of experience": years_of_experience,
        "gender": gender,
        "date of birth": date_of_birth,
        "address": address,
        "role": "agent"
    }

    users_collection.insert_one(agent)
    return {"message": "Agent registered successfully!"}