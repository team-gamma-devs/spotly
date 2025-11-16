# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Setup
```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install --no-root

# Activate virtual environment
source $(poetry env info -p)/bin/activate
```

### Running the Application
```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Production server
gunicorn app.main:app --bind 0.0.0.0:8000 --workers 2 --worker-class uvicorn.workers.UvicornWorker
```

### Database
```bash
# Start MongoDB for development
docker compose -f docker-compose.dev.yaml up -d

# Stop MongoDB
docker compose -f docker-compose.dev.yaml down -v
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/path/to/test_file.py

# Run tests with coverage
pytest --cov=app

# Run single test
pytest tests/path/to/test_file.py::test_function_name
```

### Docker Deployment
```bash
# Build and run all services (production)
docker compose build --no-cache && docker compose up -d

# Check logs
docker compose logs -f backend
```

### Environment Setup
Create a `.env` file in the project root with:
```
SECRET_KEY=<generate with: openssl rand -hex 32>
RESEND_API_KEY=<your-email-service-key>
MONGO_INITDB_ROOT_USERNAME=<mongodb-user>
MONGO_INITDB_ROOT_PASSWORD=<mongodb-password>
MONGODB_URL=mongodb://USERNAME:PASSWORD@mongo:27017
```

## Architecture Overview

Spotly is a FastAPI-based backend following **Clean Architecture** principles with the following layers:

### Layer Structure

1. **API Layer** (`app/api/`)
   - **Routes**: HTTP endpoint handlers organized by feature (auth, graduate, manager, signup)
   - **Schemas**: Pydantic request/response models for validation and serialization
   - **Middlewares**: Request logging, signature verification, CORS, global exception handling, trusted host validation
   - **Decorators**: Custom decorators for request handling

2. **Service Layer** (`app/services/`)
   - **Use Cases**: Business logic orchestration (RegisterUser, UserLogin, PostFeedback, GraduatesFilter, etc.)
   - **Schemas**: Internal data transformation schemas
   - **Exceptions**: Domain-specific exceptions for each use case
   - **Prompts**: AI service prompts and templates

3. **Domain Layer** (`app/domain/`)
   - **Models**: Core entities with validation (User, Invitation, TutorFeedback, CVInfo)
   - **Ports**: Interfaces/protocols defining contracts (IBaseRepository, EmailServicePort, AIServicePort, StoragePort)

4. **Infrastructure Layer** (`app/infrastructure/`)
   - **Database**: MongoDB repositories and connection management (BaseRepository, UserRepository, FilterRepository, InvitationRepository)
   - **Email**: Resend email service implementation
   - **AI**: Gemini AI service for CV processing
   - **Supabase**: File storage and bucket service for avatars and CVs

### Data Flow

1. **User Registration**: `POST /v1/signup/register` → RegisterUser use case → CV processing (Gemini AI) → MongoDB save
2. **Login**: `POST /v1/auth/login` → UserLogin use case → Invitation verification → JWT token generation
3. **File Uploads**: Avatar and CV files uploaded to Supabase, paths stored in MongoDB
4. **Filters**: Manager endpoints for filtering and managing graduates

### Key Patterns

- **Dependency Injection**: Services accept optional repository/service parameters for testability
- **Repository Pattern**: All database access through repository interfaces
- **Use Case Classes**: Each business operation has a dedicated use case class (e.g., RegisterUser, UserLogin)
- **Model Validation**: Domain models use property setters for validation
- **Async/Await**: FastAPI async handlers for non-blocking I/O

### Configuration

- **Settings Management** (`app/settings.py`): Environment-based configuration (DevelopmentSettings, ProductionSettings, StagingSettings)
- **Middleware Stack**: Trusted hosts → CORS → Request logging → Signature verification → Global exception handling
- **Lifespan Events**: Database connection management in `app/infrastructure/database/lifespan.py`

### External Services

- **MongoDB**: User, invitation, and filter data storage
- **Resend**: Email delivery service
- **Google Gemini**: AI-powered CV parsing and extraction
- **Supabase**: File storage for avatars and CVs

## Important Notes

- Use async/await throughout; all database operations use Motor (async MongoDB driver)
- Configuration uses Pydantic BaseSettings with `.env` file support
- Rate limiting is configured per environment (1000/min dev, 60/min production)
- CORS is strict in production, permissive in development
- MongoDB uses connection pooling (10-100 connections based on config)
- File uploads validated by size (MAX_PDF_SIZE, MAX_CSV_SIZE, MAX_IMG_SIZE from settings)
- JWT tokens: 30-minute access, 7-day refresh tokens
