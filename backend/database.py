import os

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "pdf_management_system"
)

client = None
db = None


def connect_database():
    """
    Connect to MongoDB Atlas and initialize database indexes.
    """

    global client, db

    if not MONGODB_URI:
        raise RuntimeError(
            "MONGODB_URI is missing. Check your .env file."
        )

    try:
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
        )

        # Verify the connection.
        client.admin.command("ping")

        db = client[MONGODB_DATABASE]

        # Create indexes.
        db.users.create_index(
            [("username", ASCENDING)],
            unique=True
        )

        db.processing_jobs.create_index(
            [("created_at", DESCENDING)]
        )

        db.processing_jobs.create_index(
            [("user_id", ASCENDING)]
        )

        print("MongoDB Atlas connected successfully.")

        return db

    except PyMongoError as exc:
        raise RuntimeError(
            f"Could not connect to MongoDB Atlas: {exc}"
        ) from exc


def get_database():
    if db is None:
        raise RuntimeError(
            "Database is not initialized."
        )

    return db


def close_database():
    global client, db

    if client is not None:
        client.close()

    client = None
    db = None