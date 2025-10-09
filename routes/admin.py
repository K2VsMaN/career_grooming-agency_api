from db import users_collection, application_forms_collection
from utils import replace_user_id, replace_form_id, valid_id
from fastapi import HTTPException, status, Depends
from bson.objectid import ObjectId
from fastapi import APIRouter
from dependencies.authn import is_authenticated
from dependencies.authz import has_role
from typing import Annotated

admin_router = APIRouter(tags=["Admin"])

@admin_router.get("/forms", dependencies=[Depends(has_role("admin"))])
def get_application_forms(user_id: Annotated[str, Depends(is_authenticated)]):
    valid_id(user_id)
    all_forms = application_forms_collection.find().to_list()
    return {"forms": list(map(replace_form_id, all_forms))}

@admin_router.delete("/forms/{form_id}", dependencies=[Depends(has_role("admin"))])
def delete_form(form_id):
    valid_id(form_id)
    # Delete form from database
    delete_result = application_forms_collection.delete_one(
        filter={"_id": ObjectId(form_id)})
    if not delete_result:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received")

    return {"message": f"form with id {form_id} has been deleted successfully."}



@admin_router.get("/users", dependencies=[Depends(has_role("admin"))])
def get_users(user_id: Annotated[str, Depends(is_authenticated)]):
    valid_id(user_id)
    all_users = users_collection.find().to_list()
    return {"users": list(map(replace_user_id, all_users))}


@admin_router.get("/users/{user_id}", dependencies=[Depends(has_role("admin"))])
def get_user_by_id(user_id):
    valid_id(user_id)
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    return {"data": replace_user_id(user)}


@admin_router.delete("/users/{user_id}", dependencies=[Depends(has_role("admin"))])
def delete_user(user_id):
    valid_id(user_id)
    # Delete user from database
    delete_result = users_collection.delete_one(
        filter={"_id": ObjectId(user_id)})
    if not delete_result:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received")

    return {"message": f"user with id {user_id} has been deleted successfully."}
