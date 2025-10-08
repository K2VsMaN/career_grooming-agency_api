from fastapi import APIRouter, Form, UploadFile, File
from db import users_collection
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Annotated
from enum import Enum
import bcrypt
import jwt
import os
from datetime import datetime, timedelta, timezone

users_router = APIRouter(tags=["Users"])

class UserDetails(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserRole(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"
    USER = "trainee"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

PASSCODE_REQUIRED = "CGATrainee2025"

@users_router.post("/users/signup")
def register_user(
        username: Annotated[str, Form()],
        email: Annotated[EmailStr, Form()],
        password: Annotated[str, Form(min_length=8)],
        confirm_password: Annotated[str, Form()],
        passcode: Annotated[str, Form()],
        role: Annotated[UserRole, Form()] = UserRole.USER):

    user_count = users_collection.count_documents({"email": email})
    if user_count > 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "User already exists!")

    if password != confirm_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Passwords do not match!")

    hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    if user_count["role"] == "trainee":
        if passcode != PASSCODE_REQUIRED:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Invalid or missing passcode!")

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
    password: Annotated[str, Form(min_length=8)]
):
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found!")

    correct_password = bcrypt.checkpw(password.encode(), user["password"])
    if not correct_password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong credentials!")


    encoded_jwt = jwt.encode({
            "id": str(user["_id"]),
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=60)
        }, os.getenv("JWT_SECRET_KEY"), os.getenv("JWT_ALGORITHM"))

    return {
        "message": "Login successful",
        "access_token": encoded_jwt,
        "role": user["role"]
    }


@users_router.post("/forms/trainee")
def register_trainee(
    trainee_name: Annotated[str, Form()],
    trainee_email: Annotated[EmailStr, Form()],
    trainee_phone_number: Annotated[str, Form()],
    trainee_ghana_card: Annotated[UploadFile, File()],
    trainee_birth_cert: Annotated[UploadFile, File()],
    trainee_wassce_cert: Annotated[UploadFile, File()], 
    parent_name: Annotated[str, Form()],
    parent_contact: Annotated[str, Form()],    
    parent_occupation: Annotated[str, Form()],
    parent_ghana_card: Annotated[UploadFile, File()],
    trainee_gender: Annotated[Gender, Form()] = Gender.MALE
):
    # Check if trainee already exists
    if users_collection.find_one({"email": trainee_email}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Trainee already registered!")


    # Create trainee document
    trainee = {
        "trainee_name": trainee_name,
        "trainee_email": trainee_email,
        "trainee_phone_number": trainee_phone_number,
        "trainee_ghana_card": trainee_ghana_card,
        "trainee_birth_cert": trainee_birth_cert,
        "trainee_gender": trainee_gender,
        "trainee_wassce_cert": trainee_wassce_cert,
        "parent_name": parent_name,
        "parent_contact": parent_contact,
        "parent_occupation": parent_occupation,
        "parent_ghana_card":parent_ghana_card,
        "role": "trainee"
    }

    users_collection.insert_one(trainee)
    return {"message": "Trainee registered successfully!"}


@users_router.post("/forms/agent")
def register_agent(
    full_name: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    phone_number: Annotated[str, Form()],
    profession: Annotated[str, Form()],
    company: Annotated[str, Form()],
    years_of_experience: Annotated[str, Form()],
    certificate: Annotated[UploadFile, File()],
    ghana_card: Annotated[UploadFile, File()],
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
        "profession": profession,
        "company": company,
        "years_of_experience": years_of_experience,
        "gender": gender,
        "ghana_card": ghana_card,
        "certificate": certificate,
        "role": "agent"
    }

    users_collection.insert_one(agent)
    return {"message": "Agent registered successfully!"}