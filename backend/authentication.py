
import os
import bcrypt

from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId
from fastapi import HTTPException, Request, status

from backend.database import get_database


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    """

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError(
            "Password must not exceed 72 UTF-8 bytes."
        )

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(rounds=12)
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    """
    Verify a password against its stored bcrypt hash.
    """

    try:
        password_bytes = password.encode("utf-8")

        if len(password_bytes) > 72:
            return False

        return bcrypt.checkpw(
            password_bytes,
            hashed_password.encode("utf-8")
        )

    except (ValueError, TypeError):
        return False


def create_admin_user():
    """
    Initialize or synchronize the administrator account
    using the credentials in .env.

    Important:
    - Preserve the original MongoDB user ID.
    - Preserve existing PDF history.
    - Update credentials instead of creating another admin.
    - Invalidate existing sessions when credentials change.
    """

    db = get_database()

    username = os.getenv("ADMIN_USERNAME", "admin").strip()
    password = os.getenv("ADMIN_PASSWORD")

    if not username:
        raise RuntimeError(
            "ADMIN_USERNAME cannot be empty."
        )

    if not password:
        raise RuntimeError(
            "ADMIN_PASSWORD is missing from .env."
        )

    if len(password.encode("utf-8")) > 72:
        raise RuntimeError(
            "ADMIN_PASSWORD must not exceed 72 UTF-8 bytes."
        )

    # Find existing administrator accounts.
    # The oldest account is treated as the original account.
    administrators = list(
        db.users.find(
            {"role": "admin"}
        ).sort("created_at", 1)
    )

    # First-time installation.
    if not administrators:

        existing_username = db.users.find_one({
            "username": username
        })

        if existing_username:
            raise RuntimeError(
                "The configured administrator username "
                "already belongs to another account."
            )

        db.users.insert_one({
            "username": username,
            "password_hash": hash_password(password),
            "role": "admin",
            "session_version": 0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc)
        })

        print(
            f"Administrator account '{username}' created."
        )

        return

    # Preserve the original administrator document and its _id.
    original_admin = administrators[0]
    original_admin_id = original_admin["_id"]

    # Check whether the requested username belongs to another user.
    username_owner = db.users.find_one({
        "username": username
    })

    if (
        username_owner
        and username_owner["_id"] != original_admin_id
    ):

        # If it is a previously-created duplicate administrator,
        # disable it without deleting its MongoDB document.
        if username_owner.get("role") == "admin":

            duplicate_id = username_owner["_id"]

            replacement_username = (
                f"disabled-admin-{duplicate_id}"
            )

            db.users.update_one(
                {"_id": duplicate_id},
                {
                    "$set": {
                        "username": replacement_username,
                        "is_active": False
                    },
                    "$inc": {
                        "session_version": 1
                    }
                }
            )

            print(
                "A duplicate administrator account was disabled."
            )

        else:
            raise RuntimeError(
                "The username configured in .env already "
                "belongs to a non-administrator account. "
                "Choose another username."
            )

    # Check whether the configured credentials have changed.
    username_changed = (
        original_admin.get("username") != username
    )

    password_matches = verify_password(
        password,
        original_admin.get("password_hash", "")
    )

    password_changed = not password_matches

    credentials_changed = (
        username_changed or password_changed
    )

    update_fields = {
        "username": username,
        "is_active": True
    }

    if password_changed:
        update_fields["password_hash"] = hash_password(password)

    # Ensure older accounts have a session version.
    if "session_version" not in original_admin:
        db.users.update_one(
            {"_id": original_admin_id},
            {
                "$set": {
                    "session_version": 0
                }
            }
        )

    if credentials_changed:

        db.users.update_one(
            {"_id": original_admin_id},
            {
                "$set": update_fields,
                "$inc": {
                    "session_version": 1
                }
            }
        )

        print(
            "Administrator credentials updated successfully."
        )

        print(
            "All previously issued administrator sessions "
            "have been invalidated."
        )

    else:

        # Keep the account active and ensure the session field exists.
        db.users.update_one(
            {"_id": original_admin_id},
            {
                "$set": {
                    "is_active": True
                },
                "$setOnInsert": {
                    "session_version": 0
                }
            }
        )

        print(
            f"Administrator account '{username}' is up to date."
        )


def authenticate_user(
    username: str,
    password: str
):
    """
    Authenticate a user using username and password.
    """

    db = get_database()

    user = db.users.find_one({
        "username": username.strip(),
        "is_active": {"$ne": False}
    })

    if not user:
        return None

    if not verify_password(
        password,
        user.get("password_hash", "")
    ):
        return None

    return user


def get_current_user(request: Request):
    """
    Retrieve and validate the authenticated user.

    Every protected request checks the session version
    against the latest version stored in MongoDB.
    """

    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required."
        )

    try:
        object_id = ObjectId(user_id)

    except Exception:
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is no longer valid."
        )

    db = get_database()

    user = db.users.find_one({
        "_id": object_id
    })

    if not user or user.get("is_active") is False:
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is no longer valid."
        )

    current_version = int(
        user.get("session_version", 0)
    )

    session_version = request.session.get(
        "session_version"
    )

    if session_version is None:
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session has expired. Please sign in again."
        )

    try:
        session_version = int(session_version)

    except (ValueError, TypeError):
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is no longer valid."
        )

    if session_version != current_version:
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your credentials have changed. Please sign in again."
        )

    return user
