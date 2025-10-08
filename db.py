from pymongo import MongoClient
import os
from dotenv import load_dotenv


load_dotenv()

#Connect to Mongo Atlas Cluster
mongo_client = MongoClient(os.getenv("MONGO_URI"))


# Access database
career_grooming_db = mongo_client["career_grooming_db"]


# Pick a connection to operate on
career_grooming_collection = career_grooming_db["adverts"]
users_collection = career_grooming_db["users"]
