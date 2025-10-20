from bson.objectid import ObjectId
from fastapi import HTTPException, status
from google import genai
from dotenv import load_dotenv

load_dotenv()

genai_client = genai.Client()

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

def serialize_user(user):
    if not user:
        return None
    user["_id"] = str(user["_id"])
    return user


def serialize_mongo_data(data):
    if isinstance(data, list):
        return [serialize_mongo_data(item) for item in data]
    elif isinstance(data, dict):
        return {
            key: serialize_mongo_data(value)
            for key, value in data.items()
        }
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data