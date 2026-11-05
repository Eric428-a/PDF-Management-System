
# PDF Management System

A web-based PDF inspection, compression, and management platform built with **Python, FastAPI, HTML, CSS, JavaScript, and MongoDB Atlas**.

The application provides an administrator dashboard for uploading PDF documents, inspecting their properties, compressing them toward a configurable target size, downloading original or compressed files, and reviewing processing history and dashboard statistics.

<p align="center">
  <img src="docs/images/system-architecture.png" alt="PDF Management System Architecture" width="850">
</p>

<p align="center">
  <strong>PDF Inspection | Intelligent Compression | Document Management</strong>
</p>

---

## Table of Contents

- [Project Demonstration](#project-demonstration)
- [Application Screenshots](#application-screenshots)
- [System Architecture](#system-architecture)
- [Application Workflow](#application-workflow)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation and Setup](#installation-and-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Using the Application](#using-the-application)
- [API Documentation](#api-documentation)
- [File Storage and Database](#file-storage-and-database)
- [PDF Compression Engine](#pdf-compression-engine)
- [Security Considerations](#security-considerations)
- [Deployment](#deployment)
- [Learning Resources](#learning-resources)
- [License](#license)

---

## Project Demonstration

Watch the PDF Management System in action.

<!-- Replace YOUR_YOUTUBE_VIDEO_ID with the ID of your actual YouTube demonstration video. -->

<p align="center">
  <a href="[![https://www.youtube.com/watch?v=YOUR_YOUTUBE_VIDEO_ID](http://youtube.com/watch?v=AFHfNY2iu2I)]">
    <img src="(https://www.youtube.com/watch?v=AFHfNY2iu2I)"
         alt="Watch PDF Management System demonstration"
         width="800">
  </a>
</p>

<p align="center">
  <strong>
    <a href="https://www.youtube.com/watch?v=YOUR_YOUTUBE_VIDEO_ID">
      Watch the Project Demonstration on YouTube
    </a>
  </strong>
</p>

> GitHub README files do not normally support an embedded YouTube player. The thumbnail above provides a clickable link to the video.

**Video coverage:**

- Administrator login.
- Dashboard overview.
- PDF uploading.
- PDF inspection.
- PDF compression.
- Compression results.
- Downloading processed documents.
- Processing history.

---

## Application Screenshots

The following screenshots demonstrate the application's actual user interface and functionality.

All screenshots are stored in the `docs/images/` directory.

### 1. Login Interface

![PDF Management System Login](docs/images/login-page.png)

The administrator login interface provides access to the PDF management dashboard.

### 2. Dashboard Overview

![PDF Management System Dashboard](docs/images/dashboard-overview.png)

The dashboard provides an overview of uploaded documents, compression activity, target achievements, and storage savings.

### 3. PDF Upload

![PDF Upload Interface](docs/images/pdf-upload.png)

Administrators can select and upload PDF documents for inspection and processing.

### 4. PDF Inspection

![PDF Inspection Interface](docs/images/pdf-inspection.png)

The inspection functionality examines PDF documents and displays available document information.

### 5. Compression Results

![PDF Compression Results](docs/images/compression-results.png)

The compression results interface displays the outcome of the PDF processing operation.

### 6. Processing History

![PDF Processing History](docs/images/processing-history.png)

The processing history provides access to previously processed PDF jobs.

### 7. Compression Comparison

![PDF Compression Comparison](docs/images/compression-comparison.png)

A comparison of original and compressed PDF file sizes demonstrates the effectiveness of the compression process.

---

## System Architecture

The PDF Management System follows a modular architecture consisting of a frontend, backend, database, PDF processing modules, and local file storage.

![PDF Management System Architecture](docs/images/system-architecture.png)

### Architecture Components

| Component | Technology | Responsibility |
|---|---|---|
| Frontend | HTML, CSS, JavaScript | User interface and dashboard interactions |
| Backend | Python, FastAPI | Application logic and API endpoints |
| Authentication | bcrypt and secure session cookies | Administrator authentication |
| PDF Inspection | PyMuPDF | PDF inspection and document information |
| PDF Compression | PyMuPDF and Pillow | PDF and image processing |
| Database | MongoDB Atlas | Administrator accounts and processing metadata |
| File Storage | Local filesystem | Original and compressed PDF files |

### Frontend

The frontend provides the application's user interface, including:

- Administrator login.
- Dashboard.
- PDF upload interface.
- PDF inspection interface.
- Compression results.
- Processing history.

### Backend

The FastAPI backend manages:

- Authentication and session validation.
- PDF uploads.
- File validation.
- PDF inspection.
- PDF compression.
- File downloads.
- Processing history.
- Dashboard statistics.

### Database

MongoDB Atlas stores application information, including administrator accounts and PDF processing metadata.

### File Storage

The application maintains separate directories for original and compressed PDF documents.

---

## Application Workflow

The following diagram illustrates the main PDF processing workflow.

![PDF Management System Workflow](docs/images/application-workflow.png)

### Processing Steps

1. **Administrator Login:** The administrator authenticates using configured credentials.
2. **PDF Upload:** A PDF document is selected and uploaded.
3. **File Validation:** The backend validates the uploaded document.
4. **PDF Inspection:** The system examines the PDF and retrieves available document information.
5. **PDF Compression:** The compression engine applies an appropriate processing strategy.
6. **Output Verification:** The generated PDF is checked and its compression result evaluated.
7. **Save Results:** The compressed document is stored and processing metadata is recorded.
8. **Download:** The administrator can download the original or compressed document.

---

## Features

### Administrator Authentication

- Administrator login.
- Password hashing using bcrypt.
- Session-based authentication.
- Protected application routes.

### PDF Management

- PDF document uploading.
- File type and size validation.
- PDF inspection.
- Original PDF downloads.
- Compressed PDF downloads.

### Intelligent PDF Compression

- Native PDF optimization where appropriate.
- Selective image compression where applicable.
- RGB colour-preserving raster compression paths.
- Evaluation of different compression settings.
- Configurable target file size.
- Output verification.
- Protection against replacing an original file with a larger unsuccessful result.

### Dashboard and Reporting

- Total uploaded PDFs.
- Number of compressed PDFs.
- Target achievement statistics.
- Storage savings.
- Processing history.

---

## Technology Stack

| Category | Technology |
|---|---|
| Frontend | HTML5 |
| Styling | CSS3 |
| Frontend scripting | JavaScript |
| Backend | Python |
| Web framework | FastAPI |
| Database | MongoDB Atlas |
| PDF processing | PyMuPDF |
| Image processing | Pillow |
| Password hashing | bcrypt |
| Session management | Secure session cookies |
| Version control | Git and GitHub |

---

## Project Structure

```text
PDF-MANAGEMENT-SYSTEM/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── authentication.py
│   ├── pdf_inspector.py
│   ├── pdf_compressor.py
│   ├── file_manager.py
│   └── requirements.txt
│
├── frontend/
│   ├── login.html
│   ├── dashboard.html
│   ├── favicon.svg
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dashboard.js
│
├── storage/
│   ├── uploads/
│   │   └── .gitkeep
│   └── compressed/
│       └── .gitkeep
│
├── docs/
│   └── images/
│       ├── README.md
│       ├── login-page.png
│       ├── dashboard-overview.png
│       ├── pdf-upload.png
│       ├── pdf-inspection.png
│       ├── compression-results.png
│       ├── processing-history.png
│       ├── compression-comparison.png
│       ├── system-architecture.png
│       └── application-workflow.png
│
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

**Important:** The actual `.env` file is created locally and must not be committed to the public repository.

---

## Requirements

Before installing the application, ensure that you have:

- Python 3.10 or newer.
- Git.
- A MongoDB Atlas account.
- Internet access for MongoDB Atlas connectivity.
- A code editor such as Visual Studio Code.

---

## Installation and Setup

### 1. Clone the Repository

Replace `YOUR_GITHUB_USERNAME` with your GitHub username or organization.

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/pdf-management-system.git

cd pdf-management-system
```

Alternatively, download the repository ZIP and extract it.

### 2. Create a Virtual Environment

From the project root:

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

**Windows Command Prompt:**

```bat
.venv\Scripts\activate
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux and macOS:**

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

Run this command from the project root:

```bash
python -m pip install -r backend/requirements.txt
```

---

## Environment Configuration

The application uses environment variables to manage database connectivity, administrator credentials, session security, and upload configuration.

### 1. Create the Environment File

Copy `.env.example` to `.env`.

**Windows:**

```bat
copy .env.example .env
```

**Linux and macOS:**

```bash
cp .env.example .env
```

### 2. Configure Environment Variables

Update the values in your local `.env` file:

```dotenv
APP_ENV=development

MONGODB_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/?retryWrites=true&w=majority

MONGODB_DATABASE=pdf_management_system

ADMIN_USERNAME=admin
ADMIN_PASSWORD=REPLACE_WITH_A_STRONG_PASSWORD

SESSION_SECRET=REPLACE_WITH_A_LONG_RANDOM_SECRET

MAX_UPLOAD_MB=50

DEFAULT_TARGET_KB=500
```

### Environment Variables Explained

| Variable | Description |
|---|---|
| `APP_ENV` | Application environment. |
| `MONGODB_URI` | MongoDB Atlas connection string. |
| `MONGODB_DATABASE` | Database name. |
| `ADMIN_USERNAME` | Configured administrator username. |
| `ADMIN_PASSWORD` | Configured administrator password. |
| `SESSION_SECRET` | Secret used for session protection. |
| `MAX_UPLOAD_MB` | Maximum permitted PDF upload size in megabytes. |
| `DEFAULT_TARGET_KB` | Default compression target in kilobytes. |

### 3. Generate a Secure Session Secret

Generate a random secret locally:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated value into your `.env` file.

### 4. Configure MongoDB Atlas

1. Create a MongoDB Atlas account.
2. Create a project and database cluster.
3. Create a database user.
4. Configure network access to allow your development machine to connect.
5. Copy your MongoDB connection string.
6. Update `MONGODB_URI` in `.env`.
7. Replace the placeholder credentials with your own.

Never publish your actual MongoDB connection string.

---

## Running the Application

Ensure that:

- Your virtual environment is activated.
- Dependencies are installed.
- Your `.env` file is configured.
- MongoDB Atlas is accessible.

From the project root, run:

```bash
python -m uvicorn backend.main:app --reload
```

Open your browser:

```text
http://127.0.0.1:8000
```

The `--reload` option is intended for local development.

---

## Using the Application

The typical application workflow is:

1. Open the application in your browser.
2. Sign in using the configured administrator credentials.
3. Select a PDF document.
4. Upload the document.
5. Inspect the PDF.
6. Set or use the configured compression target.
7. Start the compression process.
8. Review the compression results.
9. Download the original or compressed PDF.
10. Review previous jobs through processing history.

---

## API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

### Main API Functionality

The application provides endpoints for:

- Administrator login.
- Administrator logout.
- Current administrator information.
- PDF upload and inspection.
- PDF compression.
- Original PDF downloads.
- Compressed PDF downloads.
- Processing history.
- Dashboard statistics.
- Application health checks.

---

## File Storage and Database

### Original PDF Files

Original uploaded PDFs are stored in:

```text
storage/uploads/
```

### Compressed PDF Files

Generated compressed PDFs are stored in:

```text
storage/compressed/
```

### MongoDB Atlas

MongoDB Atlas stores application records such as:

- Administrator account information.
- PDF processing metadata.
- Compression statistics.
- Processing history.

The PDF binary files are maintained in the local storage directories rather than being stored directly in MongoDB.

### Storage Persistence

The local storage arrangement is suitable for development.

For production hosting, remember that some platforms use ephemeral filesystems. Files may disappear when an application instance restarts or is replaced.

Configure a persistent disk or suitable object-storage service before relying on production file storage.

---

## PDF Compression Engine

The PDF compression engine is designed to reduce document size while considering readability, colour preservation, and document integrity.

The processing strategies include:

- Native PDF optimization where appropriate.
- Selective compression of suitable embedded images.
- RGB colour-preserving raster compression paths.
- Evaluation of different DPI and JPEG quality settings.
- Configurable target file sizes.
- Output verification.
- Protection against keeping a larger unsuccessful compression result.

### Compression Considerations

Compression results depend on the source PDF.

Different document types behave differently:

- Scanned PDFs often contain large embedded images.
- Text-based PDFs may already be highly optimized.
- Vector-heavy documents may not benefit from rasterization.
- Image-heavy documents may offer greater opportunities for compression.

A requested target size is a goal rather than a guarantee.

Aggressive compression can affect image quality, and rasterization can remove selectable text and other document features. Important documents should always be reviewed after compression.

---

## Security Considerations

This repository is public, so protecting credentials and uploaded documents is essential.

- Never commit `.env`.
- Commit `.env.example` with placeholder values only.
- Never publish MongoDB credentials.
- Never publish administrator passwords.
- Never publish session secrets.
- Do not commit private or confidential PDF documents.
- Keep uploaded and compressed files out of Git.
- Use strong administrator credentials.
- Use HTTPS in production.
- Configure secure session cookies in production.
- Restrict MongoDB Atlas network access and database permissions.
- Review screenshots before publishing them.

---

## Deployment

The application can be prepared for deployment on a hosting platform such as Render.

### Production Deployment Considerations

1. Configure environment variables in the hosting platform.
2. Set `APP_ENV=production`.
3. Generate a strong and unique `SESSION_SECRET`.
4. Configure MongoDB Atlas connectivity.
5. Enable HTTPS.
6. Configure secure session-cookie settings.
7. Configure persistent file storage or object storage.
8. Confirm the production start command.
9. Install all required Python dependencies.
10. Test authentication, uploading, inspection, compression, downloads, and processing history.

### Important Storage Note

A standard ephemeral application filesystem should not be treated as permanent PDF storage.

Use a persistent disk or object-storage service for production documents.

---

## Learning Resources

The following resources can help developers understand the technologies and concepts used in this project.

### Official Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [MongoDB Atlas Documentation](https://www.mongodb.com/docs/atlas/)
- [Python Documentation](https://docs.python.org/3/)

### YouTube Tutorials

Additional YouTube tutorials covering FastAPI, PDF processing, Python, and MongoDB can be added here.

Third-party tutorials are provided for educational purposes and are not official demonstrations of this application.

---

## License

This project is distributed under the **Boost Software License 1.0 (BSL-1.0)**, subject to the terms contained in the [`LICENSE`](LICENSE) file.

Please review the license before using, modifying, or redistributing this project.

---

<p align="center">
  <strong>PDF Management System</strong>
  <br>
  Built with Python, FastAPI, JavaScript, and MongoDB Atlas.
</p>
