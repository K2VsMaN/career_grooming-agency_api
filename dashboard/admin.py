from db import users_collection, application_forms_collection
from utils import replace_form_id, valid_id, two_valid_ids, serialize_mongo_data, serialize_user
from fastapi import HTTPException, status, Depends, Form
from bson.objectid import ObjectId
from fastapi import APIRouter
from dependencies.authn import is_authenticated
from dependencies.authz import has_roles
from typing import Annotated
from email.message import EmailMessage
from pydantic import EmailStr
import smtplib
import os

admin_router = APIRouter(tags=["Admin"])

trainee_code = os.getenv("TRAINEE_PASSCODE")
agent_code = os.getenv("AGENT_PASSCODE")


@admin_router.post("/admin/send_verification_code", dependencies=[Depends(has_roles("admin"))])
def send_verification_code(email: Annotated[EmailStr, Form()]):
    # Ensure application exist
    user = application_forms_collection.find_one(
        filter={"$or": [{"trainee_email": email}, {"email": email}]})
    print(user)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            "Applicant does not exist!")
    # elif not agent:

    #     raise HTTPException(status.HTTP_404_NOT_FOUND, "Applicant does not exist!")
    # Create the email message
    msg = EmailMessage()
    msg["From"] = "noreply@example.com"

    msg["Subject"] = "[Important] Verification Code"
    if user["role"] == "trainee":
        msg["To"] = user["trainee_email"]
        msg.set_content(
            f"Dear {user["trainee_name"]},\nCongratulations {user["trainee_name"]}!\n Use this passcode to signup {trainee_code}"
        )
    elif user["role"] == "agent":
        msg["To"] = user["email"]
        msg.set_content(
            f"Dear {user["full_name"]},\nCongratulation {user["full_name"]}!\n Use this passcode to signup {agent_code}"
        )
    # Send password reset email
    try:
        with smtplib.SMTP(os.getenv("SMTP_HOST"), os.getenv("SMTP_PORT")) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USERNAME"),
                         os.getenv("SMTP_PASSWORD"))
            server.send_message(msg=msg)
        # Return reponse
        return {"message": "Passcode sent successfully!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED, detail=e)


@admin_router.post("admin/assign_agent/{agent_id}", dependencies=[Depends(has_roles("admin"))])
def assign_trainee_to_agent(agent_id, trainee_id):
    two_valid_ids(agent_id, trainee_id)
    agent_found = users_collection.find_one(
        {"_id": ObjectId(agent_id), "role": "agent"})
    if not agent_found:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="Agent not found")

    trainee_found = users_collection.find_one(
        {"_id": ObjectId(trainee_id), "role": "trainee"})
    if not trainee_found:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="Trainee not found")

    if trainee_found.get("agent_id") is not None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Trainee '{trainee_found['username']}' is already assigned to an agent."
        )

    max_trainees = 5

    if len(agent_found.get("trainees_assigned", [])) >= max_trainees:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Agent '{agent_found['username']}' has reached the maximum assignment limit of {max_trainees}."
        )

    users_collection.update_one({
        "_id": ObjectId(trainee_id),
        "role": "trainee"},
        {"$set": {
            "agent_id": agent_found["_id"],
            "agent_name": agent_found["username"],
            "agent_email": agent_found["email"]
        }})

    users_collection.update_one(
        {
            "_id": ObjectId(agent_id),
            "role": "trainee"},
        {"$set": {
            "trainee_id": trainee_found["_id"],
            "trainee_name": trainee_found["username"],
            "trainee_email": trainee_found["email"]
        }}
    )

    return {"message": f"Agent '{agent_found["username"]}' has been assigned to '{trainee_found["username"]}'"}


@admin_router.get("admin/forms", dependencies=[Depends(has_roles("admin"))])
def get_application_forms(user_id: Annotated[str, Depends(is_authenticated)]):
    valid_id(user_id)
    all_forms = application_forms_collection.find().to_list()
    return {"forms": list(map(replace_form_id, all_forms))}


@admin_router.delete("admin/forms/{form_id}", dependencies=[Depends(has_roles("admin"))])
def delete_form(form_id):
    valid_id(form_id)
    # Delete form from database
    delete_result = application_forms_collection.delete_one(
        filter={"_id": ObjectId(form_id)})
    if not delete_result:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received")

    return {"message": f"form with id {form_id} has been deleted successfully."}


@admin_router.get("admin/users", dependencies=[Depends(has_roles("admin"))])
def get_users(user_id: Annotated[str, Depends(is_authenticated)]):
    valid_id(user_id)
    all_users = list(users_collection.find())
    serialized_users = serialize_mongo_data(all_users)

    return {"users": serialized_users}


@admin_router.get("admin/users/{user_id}", dependencies=[Depends(has_roles("admin"))])
def get_user_by_id(user_id: str):
    valid_id(user_id)
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"user": serialize_user(user)}


@admin_router.delete("admin/users/{user_id}", dependencies=[Depends(has_roles("admin"))])
def delete_user(user_id):
    valid_id(user_id)
    # Delete user from database
    delete_result = users_collection.delete_one(
        filter={"_id": ObjectId(user_id)})
    if not delete_result:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received")

    return {"message": f"user with id {user_id} has been deleted successfully."}

