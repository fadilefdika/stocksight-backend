import pymongo
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

# Initialize MongoDB client
client = pymongo.MongoClient(MONGODB_URI)
database = client[MONGODB_DB]
