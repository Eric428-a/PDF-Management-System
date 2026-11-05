
import os
import uuid

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

STORAGE_DIR = PROJECT_ROOT / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
COMPRESSED_DIR = STORAGE_DIR / "compressed"

MAX_UPLOAD_MB = int(
    os.getenv("MAX_UPLOAD_MB", "50")
)

MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


def initialize_storage():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    COMPRESSED_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(original_filename, file_content):
    if not original_filename:
        raise ValueError("Filename is required.")

    if not original_filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are allowed.")

    if not file_content:
        raise ValueError("The uploaded file is empty.")

    if len(file_content) > MAX_UPLOAD_BYTES:
        raise ValueError(
            f"File exceeds the {MAX_UPLOAD_MB} MB upload limit."
        )

    if not file_content.startswith(b"%PDF-"):
        raise ValueError("The uploaded file is not a valid PDF.")

    job_id = str(uuid.uuid4())
    safe_filename = f"{job_id}.pdf"

    destination = UPLOAD_DIR / safe_filename
    destination.write_bytes(file_content)

    return {
        "job_id": job_id,
        "filename": safe_filename,
        "path": destination,
        "size": len(file_content)
    }


def get_compressed_path(job_id):
    return COMPRESSED_DIR / f"{job_id}_compressed.pdf"


def get_safe_storage_path(filename, folder="uploads"):
    """
    Resolve a stored PDF inside its designated storage folder.
    """

    if not filename or Path(filename).name != filename:
        raise ValueError("Invalid storage filename.")

    allowed_directories = {
        "uploads": UPLOAD_DIR,
        "compressed": COMPRESSED_DIR
    }

    if folder not in allowed_directories:
        raise ValueError("Invalid storage directory.")

    base_directory = allowed_directories[folder].resolve()
    candidate = (base_directory / filename).resolve()

    if candidate.parent != base_directory:
        raise ValueError("Invalid storage path.")

    if not candidate.is_file():
        raise FileNotFoundError(
            f"Stored file does not exist: {filename}"
        )

    return candidate


def delete_file(path):
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        pass
