# AP-Backend

## Overview
Backend API service for the Advocacia Proativa platform. This service provides endpoints for managing legal documents, templates, and user authentication.

## Features
- User authentication using JWT tokens
- Document management (creation, retrieval, updating)
- Template management with variable extraction
- Test mode for development

## Installation

### Prerequisites
- Python 3.9+
- SQLite3

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/ap-backend.git
cd ap-backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (if applicable)
# python manage.py migrate

# Start the server
python -m uvicorn app.main:app --reload --port 8080
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token

### Documents
- `GET /api/v1/documents` - Get all user documents
- `GET /api/v1/documents/{document_id}` - Get document by ID
- `POST /api/v1/documents` - Create new document
- `PUT /api/v1/documents/{document_id}` - Update document

### Templates
- `GET /api/v1/documents/templates` - Get all templates
- `GET /api/v1/documents/templates/{template_id}` - Get template details

## Development

### Test Mode
The API includes a test mode for development purposes. To enable test mode, set the `TEST_MODE` flag to `True` in `app/core/config.py`.

## License
[MIT License](LICENSE)
