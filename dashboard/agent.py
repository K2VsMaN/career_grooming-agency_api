from db import transcript_collection, resources, trainees_collection, tasks_collection
from utils import replace_form_id, two_valid_ids, valid_id
from fastapi import Depends, File, Form
from fastapi import APIRouter, HTTPException, status
from dependencies.authn import is_authenticated
from dependencies.authz import has_role
from typing import Annotated
from bson.objectid import ObjectId
import cloudinary.uploader

agent_router = APIRouter(tags=["Agent Dashboard"])


@agent_router.post("/dashboard/agent/trainees", dependencies=[Depends(has_role("agent"))])
def get_assigned_trainees(user_id: Annotated[str, Depends(is_authenticated)]):

    valid_id(user_id)
    assigned_trainees = list(trainees_collection.find({"agent_id": ObjectId(user_id)}))
    for t in assigned_trainees:
        t["_id"] = str(t["_id"])
    return {"assigned_trainees": assigned_trainees}

@agent_router.get("/dashboard/agent/trainee/{trainee_id}/progress", dependencies=[Depends(has_role("agent"))])
def get_trainee_progress(trainee_id: str, user_id: Annotated[str, Depends(is_authenticated)]):
    two_valid_ids(trainee_id, user_id)
    progress_records = list(resources.find({"trainee_id": ObjectId(trainee_id)}))
    for p in progress_records:
        p["_id"] = str(p["_id"])
    return {"trainee_progress": progress_records}
   
@agent_router.get("/dashboard/agent/resources", dependencies=[Depends(has_role("agent"))])
def get_all_resources(user_id: Annotated[str, Depends(is_authenticated)]):
    valid_id(user_id)
    all_resources = list(resources.find({}))

    for resource in all_resources:
        resource["_id"] = str(resource["_id"])
    
    return {"resources": all_resources}

@agent_router.get("/dashboard/agent/tasks", dependencies=[Depends(has_role("agent"))])
def get_all_assigned_tasks(user_id: Annotated[str, Depends(is_authenticated)]):
    valid_id(user_id)
    assigned_tasks = list(tasks_collection.find({"agent_id": ObjectId(user_id)}))
    
    for task in assigned_tasks:
        task["_id"] = str(task["_id"])
        task["agent_id"] = str(task["agent_id"])
        task["trainee_id"] = str(task["trainee_id"])
    
    return {"assigned_tasks": assigned_tasks}

@agent_router.post("/dashboard/agent/tasks/assign", dependencies=[Depends(has_role("agent"))])
def assign_task(
    user_id: Annotated[str, Depends(is_authenticated)],
    trainee_id: Annotated[str, Form(...)],
    task_type: Annotated[str, Form(...)]  
):
    two_valid_ids(trainee_id, user_id)

    if task_type.lower() not in ["quiz", "resource"]:
        raise HTTPException(status_code=400, detail="Invalid task type")

    task_doc = {
        "agent_id": ObjectId(user_id),
        "trainee_id": ObjectId(trainee_id),
        "task_type": task_type.lower(),
        "status": "assigned"
    }

    tasks_collection.insert_one(task_doc)
    return {"message": f"{task_type.capitalize()} assigned successfully"}

@agent_router.delete("/dashboard/agent/tasks/remove", dependencies=[Depends(has_role("agent"))])
def remove_task(
    user_id: Annotated[str, Depends(is_authenticated)],
    task_id: Annotated[str, Form(...)]
):
    valid_id(task_id)
    task = tasks_collection.find_one({"_id": ObjectId(task_id), "agent_id": ObjectId(user_id)})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or unauthorized")

    tasks_collection.delete_one({"_id": ObjectId(task_id)})
    return {"message": "Task removed successfully"}

@agent_router.get("/dashboard/agent/transcript/{trainee_id}", dependencies=[Depends(has_role("agent"))])
def get_transcript(trainee_id: str, user_id: Annotated[str, Depends(is_authenticated)]):
    two_valid_ids(trainee_id, user_id)
    transcript = transcript_collection.find_one({"trainee_id": ObjectId(trainee_id)})
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return {"transcript_url": transcript["transcript_url"]}