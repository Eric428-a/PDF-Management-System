# PDF Management System

A web-based PDF inspection and compression system.

## Technology

- Frontend: HTML, CSS and JavaScript
- Backend: Python and FastAPI
- Database: MongoDB Atlas
- PDF processing: PyMuPDF
- Image processing: Pillow
- Authentication: bcrypt and secure session cookies

## Features

- Administrator login
- PDF upload
- PDF inspection
- RGB colour-preserving compression
- Automatic compression target
- PDF downloads
- Processing history
- Dashboard statistics

## Requirements

- Python 3.10 or newer
- MongoDB Atlas account
- Internet connection for Atlas database access

## Installation

Clone or open the project directory.

Create a virtual environment:

    python -m venv .venv

Activate it on Windows:

    .venv\Scripts\activate

Activate it on Linux or macOS:

    source .venv/bin/activate

Install dependencies:

    pip install -r backend/requirements.txt

## Environment

Create a .env file in the project root.

Configure:

    MONGODB_URI=your_mongodb_atlas_connection_string
    MONGODB_DATABASE=pdf_management_system
    ADMIN_USERNAME=admin
    ADMIN_PASSWORD=your_strong_password
    SESSION_SECRET=your_long_random_secret
    APP_ENV=development
    MAX_UPLOAD_MB=50
    DEFAULT_TARGET_KB=500

Never commit the .env file.

## Run the application

From the project root:

    python -m uvicorn backend.main:app --reload

Open:

    http://127.0.0.1:8000

## API documentation

FastAPI automatically provides interactive API documentation:

    http://127.0.0.1:8000/docs

## Storage

Original uploaded PDFs are stored in:

    storage/uploads/

Compressed PDFs are stored in:

    storage/compressed/

MongoDB stores user accounts and processing metadata.

## Compression

The compression engine:

- Uses RGB colour rendering.
- Preserves original page dimensions.
- Retains all pages.
- Tests multiple DPI and JPEG quality combinations.
- Stops when the requested target size is achieved.
- Reports when the target cannot be achieved.

## Deployment

The application can later be deployed to Render.

For production deployment:

- Configure environment variables in Render.
- Set APP_ENV=production.
- Use HTTPS.
- Configure persistent file storage or cloud object storage.
- Never commit secrets or uploaded documents.

## Create these two empty files as well:
 - storage/uploads/.gitkeep
 - storage/compressed/.gitkeep