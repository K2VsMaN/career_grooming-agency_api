from db import application_forms_collection, transcript_collection, resources
from utils import replace_form_id, two_valid_ids, valid_id
from fastapi import Depends, File, Form
from fastapi import APIRouter
from dependencies.authn import is_authenticated
from dependencies.authz import has_roles
from typing import Annotated
from bson.objectid import ObjectId
import cloudinary.uploader

trainee_router = APIRouter(tags=["Trainee Dashboard"])


@trainee_router.post("/dashboard/trainee/progress", dependencies=[Depends(has_roles("trainee"))])
def mark_progress(user_id: Annotated[str, Depends(is_authenticated)], resource_id, is_accessed: Annotated[bool, Form()]):
    two_valid_ids(resource_id, user_id)

    existing_progress = resources.find_one({"user_id": ObjectId(user_id),
                                            "_id": ObjectId(resource_id),
                                            "is_accessed": is_accessed})

    if is_accessed:
        if existing_progress:
            return {"message": "Already made progress"}
        else:
            resources.insert_one({
                "user_id": user_id,
                "is_accessed": True
            })
    else:
        return {"message": "Resource not accessed yet"}


@trainee_router.get("/dashboard/trainee/progress/{resource_id}", dependencies=[Depends(has_roles(["trainee", "agent"]))])
def get_progress(resource_id, user_id: Annotated[str, Depends(is_authenticated)]):
    two_valid_ids(resource_id, user_id)
    progress = resources.find_one({
        "_id": ObjectId(resource_id), 
        "user_id": ObjectId(user_id),
    })
    progress_made = progress["is_accessed"]
    if progress_made:
        return {"message": f"Has made progress on the resource with id '{resource_id}'"}
    else:
        return {"message": "No progress made yet"}
    


@trainee_router.get("/dashboard/trainee/resources", dependencies=[Depends(has_roles("trainee"))])
def get_resources(user_id: Annotated[str, Depends(is_authenticated)]):
    valid_id(user_id)
    all_forms = application_forms_collection.find().to_list()
    return {"forms": list(map(replace_form_id, all_forms))}


@trainee_router.post("/dashboard/trainee/transcript/{user_id}", dependencies=[Depends(has_roles("trainee"))])
def upload_transcript(
    user_id: Annotated[str, Depends(is_authenticated)],
    transcript: Annotated[bytes, File()]
):
    valid_id(user_id)
    upload_result = cloudinary.uploader.upload(transcript)
    transcript_collection.insert_one({
        "transcript": upload_result["secure_url"]})
    return {"message": "Transcript uploaded successfully"}
