from db import users_collection, application_forms_collection
from utils import replace_form_id, valid_id, two_valid_ids, serialize_mongo_data, serialize_user
from fastapi import HTTPException, status, Depends, Form
from bson.objectid import ObjectId
from fastapi import APIRouter
from dependencies.authn import is_authenticated
from dependencies.authz import has_roles
from typing import Annotated
from utils import genai_client

admin_router = APIRouter(tags=["Admin"])


@admin_router.post("/assign_agent/{agent_id}", dependencies=[Depends(has_roles("admin"))])
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
        {"$addToSet": {
            "trainees_assigned": {
                "trainee_id": trainee_found["_id"],
                "trainee_name": trainee_found["username"],
                "trainee_email": trainee_found["email"]
            }
        }
        }
    )

    return {"message": f"Agent '{agent_found["username"]}' has been assigned to '{trainee_found["username"]}'"}


@admin_router.get("/forms", dependencies=[Depends(has_roles("admin"))])
def get_application_forms(user_id: Annotated[str, Depends(is_authenticated)]):
    valid_id(user_id)
    all_forms = application_forms_collection.find().to_list()
    return {"forms": list(map(replace_form_id, all_forms))}


@admin_router.delete("/forms/{form_id}", dependencies=[Depends(has_roles("admin"))])
def delete_form(form_id):
    valid_id(form_id)
    # Delete form from database
    delete_result = application_forms_collection.delete_one(
        filter={"_id": ObjectId(form_id)})
    if not delete_result:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received")

    return {"message": f"form with id {form_id} has been deleted successfully."}


@admin_router.get("/users", dependencies=[Depends(has_roles("admin"))])
def get_users(user_id: Annotated[str, Depends(is_authenticated)]):
    valid_id(user_id)
    all_users = list(users_collection.find())
    serialized_users = serialize_mongo_data(all_users)

    return {"users": serialized_users}


@admin_router.get("/users/{user_id}", dependencies=[Depends(has_roles("admin"))])
def get_user_by_id(user_id: str):
    valid_id(user_id)
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"user": serialize_user(user)}


@admin_router.delete("/users/{user_id}", dependencies=[Depends(has_roles("admin"))])
def delete_user(user_id):
    valid_id(user_id)
    # Delete user from database
    delete_result = users_collection.delete_one(
        filter={"_id": ObjectId(user_id)})
    if not delete_result:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received")

    return {"message": f"user with id {user_id} has been deleted successfully."}


@admin_router.put("/genai/generate_text", dependencies=[Depends(is_authenticated)])
def assign_trainees_to_agents_with_assistance(prompt: Annotated[str, Form()]):
    response = genai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return {
        "content": response.text
    }
