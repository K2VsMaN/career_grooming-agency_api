from db import transcript_collection, resources, users_collection
from utils import two_valid_ids, valid_id
from fastapi import Depends, Form, File
from fastapi import APIRouter, HTTPException, status
from dependencies.authn import is_authenticated
from dependencies.authz import has_roles
from typing import Annotated
from bson.objectid import ObjectId
import cloudinary.uploader


agent_router = APIRouter(tags=["Agent Dashboard"])


@agent_router.get("/dashboard/agent/trainees", dependencies=[Depends(has_roles(["agent", "admin"]))])
def get_assigned_trainees(user_id: Annotated[str, Depends(is_authenticated)]):
    valid_id(user_id)
    assigned_trainees = list(users_collection.find({"agent_id": ObjectId(user_id)}))
    for t in assigned_trainees:
        t["_id"] = str(t["_id"])
    return {"assigned_trainees": assigned_trainees}

   
@agent_router.get("/dashboard/agent/resources", dependencies=[Depends(has_roles(["agent", "admin"]))])
def get_all_resources(user_id: Annotated[str, Depends(is_authenticated)]):
    valid_id(user_id)
    all_resources = list(resources.find({}))

    for resource in all_resources:
        resource["_id"] = str(resource["_id"])
    
    return {"resources": all_resources}


@agent_router.post("/dashboard/agent/resource/assign", dependencies=[Depends(has_roles(["agent", "admin"]))])
def assign_resource(
    user_id: Annotated[str, Depends(is_authenticated)],
    trainee_id: Annotated[str, Form(...)],
    resource: Annotated[bytes, File()],
    task_type: Annotated[str, Form(...)]  
):
    two_valid_ids(trainee_id, user_id)

    if task_type.lower() not in ["quiz", "resource"]:
        raise HTTPException(status_code=400, detail="Invalid task type")
    
    upload_resource = cloudinary.uploader.upload(resource)

    task_doc = {
        "agent_id": ObjectId(user_id),
        "trainee_id": ObjectId(trainee_id),
        "resource": upload_resource["secure_url"],
        "task_type": task_type.lower(),
        "status": "assigned"
    }

    resources.insert_one(task_doc)
    return {"message": f"{task_type.capitalize()} assigned successfully"}

@agent_router.delete("/dashboard/agent/resource/remove", dependencies=[Depends(has_roles(["agent", "admin"]))])
def remove_resource(
    user_id: Annotated[str, Depends(is_authenticated)],
    resource_id: Annotated[str, Form(...)]
):
    valid_id(resource_id)
    task = resources.find_one({"_id": ObjectId(resource_id), "agent_id": ObjectId(user_id)})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or unauthorized")

    resources.delete_one({"_id": ObjectId(resource_id)})
    return {"message": "Task removed successfully"}

@agent_router.get("/dashboard/agent/transcript/{trainee_id}", dependencies=[Depends(has_roles(["agent", "admin"]))])
def get_transcript(trainee_id: str, user_id: Annotated[str, Depends(is_authenticated)]):
    two_valid_ids(trainee_id, user_id)
    transcript = transcript_collection.find_one({"trainee_id": ObjectId(trainee_id)})
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return {"transcript_url": transcript["transcript_url"]}