from pymongo import MongoClient
import os
from dotenv import load_dotenv


load_dotenv()

#Connect to Mongo Atlas Cluster
mongo_client = MongoClient(os.getenv("MONGO_URI"))


# Access database
career_grooming_db = mongo_client["career_grooming_db"]


# Pick a connection to operate on
application_forms_collection = career_grooming_db["application_forms"]
users_collection = career_grooming_db["users"]
transcript_collection = career_grooming_db["transcript"]
resources = career_grooming_db["resources"]
trainees_collection = career_grooming_db["trainees"]
tasks_collection = career_grooming_db["tasks"]
