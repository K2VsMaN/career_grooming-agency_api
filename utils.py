from bson.objectid import ObjectId
from fastapi import HTTPException, status


def replace_user_id(user):
    user["id"] = str(user["_id"])
    del user["_id"]
    return user


def replace_form_id(form):
    form["id"] = str(form["_id"])
    del form["_id"]
    return form


def valid_id(id):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received"
        )

def two_valid_ids(first_id, second_id):
    if not ObjectId.is_valid(first_id) and not ObjectId.is_valid(second_id):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received"
            )