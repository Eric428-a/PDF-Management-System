
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    File,
    HTTPException,
    Depends,
    status,
)

from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    RedirectResponse,
)

from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, Field
from pymongo import DESCENDING

from backend.database import (
    connect_database,
    get_database,
    close_database,
)

from backend.authentication import (
    authenticate_user,
    create_admin_user,
    get_current_user,
)

from backend.file_manager import (
    initialize_storage,
    save_uploaded_file,
    get_compressed_path,
    get_safe_storage_path,
    delete_file,
)

from backend.pdf_inspector import inspect_pdf
from backend.pdf_compressor import compress_pdf


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

load_dotenv(PROJECT_ROOT / ".env")

APP_ENV = os.getenv("APP_ENV", "development").lower()

SESSION_SECRET = os.getenv("SESSION_SECRET")

if not SESSION_SECRET or SESSION_SECRET.startswith("REPLACE_"):
    raise RuntimeError(
        "Set a strong SESSION_SECRET in your .env file."
    )

DEFAULT_TARGET_KB = int(
    os.getenv("DEFAULT_TARGET_KB", "500")
)

MAX_UPLOAD_MB = int(
    os.getenv("MAX_UPLOAD_MB", "50")
)


# ---------------------------------------------------------
# APPLICATION
# ---------------------------------------------------------

app = FastAPI(
    title="PDF Management System",
    description="PDF inspection and compression platform.",
    version="1.0.0",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="pdf_management_session",
    max_age=60 * 60 * 8,
    same_site="lax",
    https_only=(APP_ENV == "production"),
)

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static",
)


# ---------------------------------------------------------
# REQUEST MODELS
# ---------------------------------------------------------

class LoginRequest(BaseModel):

    username: str = Field(
        min_length=1,
        max_length=100
    )

    password: str = Field(
        min_length=1,
        max_length=200
    )


class CompressionRequest(BaseModel):

    target_kb: int = Field(
        default=DEFAULT_TARGET_KB,
        ge=50,
        le=10000
    )


# ---------------------------------------------------------
# STARTUP AND SHUTDOWN
# ---------------------------------------------------------

@app.on_event("startup")
def startup_event():

    initialize_storage()

    connect_database()

    # Synchronize the existing administrator account
    # with ADMIN_USERNAME and ADMIN_PASSWORD in .env.
    #
    # The existing MongoDB user ID is preserved.
    # Credential changes invalidate existing sessions.

    create_admin_user()

    print("PDF Management System is ready.")
    print("Open http://127.0.0.1:8000")


@app.on_event("shutdown")
def shutdown_event():

    close_database()


# ---------------------------------------------------------
# PAGE ROUTES
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def login_page():

    return FileResponse(
        FRONTEND_DIR / "login.html"
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):

    # Validate the session against the current MongoDB
    # session_version, not just the presence of user_id.

    try:

        get_current_user(request)

    except HTTPException:

        return RedirectResponse(
            url="/",
            status_code=303
        )

    return FileResponse(
        FRONTEND_DIR / "dashboard.html"
    )


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/api/health")
def health_check():

    try:

        db = get_database()

        db.command("ping")

        return {
            "status": "healthy",
            "database": "connected",
            "application": "PDF Management System"
        }

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable."
        )


# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

@app.post("/api/auth/login")
def login(
    data: LoginRequest,
    request: Request
):

    user = authenticate_user(
        data.username.strip(),
        data.password
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password."
        )

    # Remove any previous session data.
    request.session.clear()

    # Store the existing MongoDB account identity.
    request.session["user_id"] = str(user["_id"])

    request.session["username"] = user["username"]

    request.session["role"] = user.get("role", "user")

    # Store the current session version.
    # This is checked against MongoDB on every protected request.

    request.session["session_version"] = int(
        user.get("session_version", 0)
    )

    return {
        "success": True,
        "message": "Login successful.",
        "username": user["username"]
    }


@app.post("/api/auth/logout")
def logout(request: Request):

    request.session.clear()

    return {
        "success": True,
        "message": "Logged out successfully."
    }


@app.get("/api/auth/me")
def current_user(
    user=Depends(get_current_user)
):

    return {
        "authenticated": True,
        "username": user["username"],
        "role": user.get("role", "user")
    }


# ---------------------------------------------------------
# PDF UPLOAD AND INSPECTION
# ---------------------------------------------------------

@app.post("/api/files/inspect")
def upload_and_inspect(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Please select a PDF file."
        )

    saved = None

    try:

        content = file.file.read(
            MAX_UPLOAD_MB * 1024 * 1024 + 1
        )

        saved = save_uploaded_file(
            file.filename,
            content
        )

        inspection = inspect_pdf(
            saved["path"]
        )

        db = get_database()

        now = datetime.now(timezone.utc)

        job_document = {

            "job_id": saved["job_id"],

            # Preserve the existing account relationship.
            "user_id": str(user["_id"]),

            "original_filename": Path(
                file.filename
            ).name,

            "original_storage_filename": saved["filename"],

            "original_size_bytes": saved["size"],

            "inspection": inspection,

            "status": "uploaded",

            "created_at": now,

            "updated_at": now,

            "compressed_storage_filename": None,

            "compression": None,
        }

        db.processing_jobs.insert_one(
            job_document
        )

        return {

            "success": True,

            "message": "PDF uploaded and inspected successfully.",

            "job_id": saved["job_id"],

            "inspection": inspection,

            "status": "uploaded"
        }

    except ValueError as exc:

        if saved:
            delete_file(saved["path"])

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        if saved:
            delete_file(saved["path"])

        raise HTTPException(
            status_code=400,
            detail=f"Could not inspect PDF: {exc}"
        )

    finally:

        file.file.close()


# ---------------------------------------------------------
# PDF COMPRESSION
# ---------------------------------------------------------

@app.post("/api/files/{job_id}/compress")
def compress_uploaded_pdf(
    job_id: str,
    data: CompressionRequest,
    user=Depends(get_current_user)
):

    db = get_database()

    job = db.processing_jobs.find_one({

        "job_id": job_id,

        "user_id": str(user["_id"])
    })

    if not job:

        raise HTTPException(
            status_code=404,
            detail="PDF processing record not found."
        )

    output_path = get_compressed_path(job_id)

    try:

        # Retrieve the original PDF from storage/uploads/.
        original_path = get_safe_storage_path(
            job["original_storage_filename"],
            folder="uploads"
        )

        # Compress the PDF and save it in storage/compressed/.
        result = compress_pdf(
            source_path=original_path,
            output_path=output_path,
            target_kb=data.target_kb
        )

        now = datetime.now(timezone.utc)

        compression_record = {
            **result,
            "created_at": now,
        }

        db.processing_jobs.update_one(

            {
                "job_id": job_id,
                "user_id": str(user["_id"])
            },

            {
                "$set": {

                    "status": (
                        "completed"
                        if result["target_met"]
                        else "completed_above_target"
                    ),

                    "compressed_storage_filename": (
                        f"{job_id}_compressed.pdf"
                    ),

                    "compression": compression_record,

                    "updated_at": now,
                }
            }
        )

        return {

            "success": True,

            "message": (
                "Compression completed successfully."
                if result["target_met"]
                else (
                    "Compression completed, but the "
                    "target size was not reached."
                )
            ),

            "job_id": job_id,

            "compression": result,
        }

    except HTTPException:

        raise

    except Exception as exc:

        # Remove incomplete output if compression failed.
        delete_file(output_path)

        raise HTTPException(
            status_code=500,
            detail=f"Compression failed: {exc}"
        )


# ---------------------------------------------------------
# PROCESSING HISTORY
# ---------------------------------------------------------

@app.get("/api/history")
def get_history(
    user=Depends(get_current_user)
):

    db = get_database()

    records = db.processing_jobs.find(
        {
            "user_id": str(user["_id"])
        }
    ).sort(
        "created_at",
        DESCENDING
    ).limit(100)

    history = []

    for record in records:

        compression = record.get("compression") or {}

        created_at = record.get("created_at")

        history.append({

            "job_id": record["job_id"],

            "filename": record.get("original_filename"),

            "original_size_kb": round(
                record.get("original_size_bytes", 0) / 1024,
                2
            ),

            "page_count": (
                record.get("inspection", {}).get(
                    "page_count", 0
                )
            ),

            "status": record.get("status"),

            "compressed_size_kb": compression.get(
                "compressed_size_kb"
            ),

            "reduction_percent": compression.get(
                "reduction_percent"
            ),

            "target_met": compression.get(
                "target_met"
            ),

            "created_at": (
                created_at.isoformat()
                if created_at
                else None
            )
        })

    return {
        "success": True,
        "records": history
    }


# ---------------------------------------------------------
# DASHBOARD STATISTICS
# ---------------------------------------------------------

@app.get("/api/dashboard/stats")
def dashboard_stats(
    user=Depends(get_current_user)
):

    db = get_database()

    user_filter = {
        "user_id": str(user["_id"])
    }

    # Total uploaded PDFs.
    total_files = db.processing_jobs.count_documents(
        user_filter
    )

    # PDFs that have compression records.
    compressed_files = db.processing_jobs.count_documents({

        **user_filter,

        "compression.compressed_size_bytes": {
            "$exists": True
        }
    })

    # PDFs that successfully reached their target.
    target_met = db.processing_jobs.count_documents({

        **user_filter,

        "compression.target_met": True
    })

    # Only include PDFs that have actually been compressed.
    pipeline = [

        {
            "$match": {

                **user_filter,

                "compression.compressed_size_bytes": {
                    "$exists": True
                }
            }
        },

        {
            "$group": {

                "_id": None,

                "original_bytes": {
                    "$sum": "$original_size_bytes"
                },

                "compressed_bytes": {
                    "$sum": "$compression.compressed_size_bytes"
                }
            }
        }
    ]

    totals = list(
        db.processing_jobs.aggregate(pipeline)
    )

    original_bytes = 0

    compressed_bytes = 0

    if totals:

        original_bytes = totals[0].get(
            "original_bytes", 0
        ) or 0

        compressed_bytes = totals[0].get(
            "compressed_bytes", 0
        ) or 0

    saved_bytes = max(
        0,
        original_bytes - compressed_bytes
    )

    return {

        "success": True,

        "total_files": total_files,

        "compressed_files": compressed_files,

        "target_met": target_met,

        "saved_mb": round(
            saved_bytes / (1024 * 1024),
            2
        )
    }


# ---------------------------------------------------------
# DOWNLOAD ORIGINAL OR COMPRESSED PDF
# ---------------------------------------------------------

@app.get("/api/files/{job_id}/download")
def download_pdf(
    job_id: str,
    kind: str = "compressed",
    user=Depends(get_current_user)
):

    db = get_database()

    job = db.processing_jobs.find_one({

        "job_id": job_id,

        "user_id": str(user["_id"])
    })

    if not job:

        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    # Original PDF.
    if kind == "original":

        stored_filename = job.get(
            "original_storage_filename"
        )

        folder = "uploads"

        download_name = job.get(
            "original_filename",
            "original.pdf"
        )

    # Compressed PDF.
    elif kind == "compressed":

        stored_filename = job.get(
            "compressed_storage_filename"
        )

        folder = "compressed"

        download_name = "compressed.pdf"

        if not stored_filename:

            raise HTTPException(
                status_code=404,
                detail="No compressed PDF is available."
            )

    else:

        raise HTTPException(
            status_code=400,
            detail="Invalid download type."
        )

    # Retrieve the file from the correct storage directory.
    try:

        file_path = get_safe_storage_path(
            stored_filename,
            folder=folder
        )

    except (ValueError, FileNotFoundError):

        raise HTTPException(
            status_code=404,
            detail="Stored PDF is unavailable."
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=download_name
    )
