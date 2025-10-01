# Git Gud Stats - Backend App

## Purpose

This folder contains the backend logic for the Git Gud Stats project, built with FastAPI. It provides endpoints to fetch and process GitHub user statistics using both REST and GraphQL APIs.

## Architecture Overview

- **main.py**  
  Application entry point. Runs the FastAPI app created in [`app.__init__.py`](app/__init__.py).

- ****init**.py**  
  App factory (`create_app`) that sets up FastAPI, CORS, OAuth, and includes API routers.

- **settings.py**  
  Loads configuration and secrets from environment variables using Pydantic Settings.

### Subfolders

- **api/**

  - **endpoints.py**: Defines API routes for user stats and debugging.
  - **schemas.py**: Pydantic models for request/response validation.
  - **auth.py**: (Reserved for authentication logic.)
  - ****init**.py**: Package marker.

- **infraestructure/**

  - **github/**
    - **client.py**: Async client for GitHub GraphQL API.
    - **queries.py**: GraphQL queries for user data.
    - ****init**.py**: Package marker.
  - **email/**: (Reserved for email integration.)
  - ****init**.py**: Package marker.

- **routers/**

  - ****init**.py**: (Reserved for additional routers.)

- **services/**

  - **user_data_service.py**: Service for fetching and processing user data from GitHub.
  - ****init**.py**: Package marker.

- **utils/**
  - **language_stats.py**: Functions for processing language statistics from GitHub data.
  - **dependencies.py**: Helpers for authentication and request headers.
  - ****init**.py**: Package marker.

## Data Flow

1. **Request** arrives at an API endpoint in [`api.endpoints`](app/api/endpoints.py).
2. **Authentication** and headers are handled by [`utils.dependencies`](app/utils/dependencies.py).
3. **Data fetching** from GitHub is performed by [`infraestructure.github.client`](app/infraestructure/github/client.py) and processed by [`services.user_data_service`](app/services/user_data_service.py).
4. **Response** is validated and serialized using models in [`api.schemas`](app/api/schemas.py).

---

This modular structure makes the codebase maintainable and easy to extend.
