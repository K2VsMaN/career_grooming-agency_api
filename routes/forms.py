from fastapi import APIRouter, Form, File
from db import  application_forms_collection, users_collection
from fastapi import HTTPException, status
from pydantic import EmailStr
from typing import Annotated
from enum import Enum
import cloudinary.uploader

application_form_router = APIRouter(tags=["Forms"])


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

@application_form_router.post("/forms/trainee")
def register_trainee(
    trainee_name: Annotated[str, Form()],
    trainee_email: Annotated[EmailStr, Form()],
    trainee_phone_number: Annotated[str, Form()],
    parent_name: Annotated[str, Form()],
    parent_contact: Annotated[str, Form()],
    parent_occupation: Annotated[str, Form()],
    trainee_ghana_card: Annotated[bytes, File()],
    trainee_birth_cert: Annotated[bytes, File()],
    trainee_wassce_cert: Annotated[bytes, File()],
    parent_ghana_card: Annotated[bytes, File()],
    trainee_gender: Annotated[Gender, Form()] = Gender.MALE
):
    # Check if trainee already exists
    if application_forms_collection.find_one({"trainee_email": trainee_email}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Trainee already registered!")

    upload_result1 = cloudinary.uploader.upload(trainee_ghana_card)
    upload_result2 = cloudinary.uploader.upload(trainee_birth_cert)
    upload_result3 = cloudinary.uploader.upload(trainee_wassce_cert)
    upload_result4 = cloudinary.uploader.upload(parent_ghana_card)


    # Create trainee document
    trainee = {
        "trainee_name": trainee_name,
        "trainee_email": trainee_email,
        "trainee_phone_number": trainee_phone_number,
        "trainee_ghana_card": upload_result1["secure_url"],
        "trainee_birth_cert": upload_result2["secure_url"],
        "trainee_gender": trainee_gender,
        "trainee_wassce_cert": upload_result3["secure_url"],
        "parent_name": parent_name,
        "parent_contact": parent_contact,
        "parent_occupation": parent_occupation,
        "parent_ghana_card":upload_result4["secure_url"],
        "role": "trainee"
    }

    application_forms_collection.insert_one(trainee)
    return {"message": "Trainee registered successfully!"}


@application_form_router.post("/forms/agent")
def register_agent(
    full_name: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    phone_number: Annotated[str, Form()],
    profession: Annotated[str, Form()],
    years_of_experience: Annotated[str, Form()],
    certificate: Annotated[bytes, File()],
    ghana_card: Annotated[bytes, File()],
    gender: Annotated[Gender, Form()] = Gender.MALE
):
    # Check if agent already exists
    if application_forms_collection.find_one({"email": email}) or users_collection.find_one({"email": email}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Agent already registered!")

    upload_result1 = cloudinary.uploader.upload(certificate)
    upload_result2 = cloudinary.uploader.upload(ghana_card)

    # Create agent document
    agent = {
        "full_name": full_name,
        "email": email,
        "phone": phone_number,
        "profession": profession,
        "years_of_experience": years_of_experience,
        "gender": gender,
        "ghana_card": upload_result1["secure_url"],
        "certificate": upload_result2["secure_url"],
        "role": "agent"
    }

    application_forms_collection.insert_one(agent)
    return {"message": "Agent registered successfully!"}