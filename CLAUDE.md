# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lorelm is a FastAPI-based application with PostgreSQL database support, featuring LLM integration and RAG capabilities. The project follows a clean architecture with clear separation of concerns.

## Common Development Commands

### Backend Development
```bash
# Install dependencies
uv sync

# Run the development server
uv run uvicorn backend:app --host 0.0.0.0 --port 8888 --reload

# Run with gunicorn (production)
uv run gunicorn backend:app -w 4 -k uvicorn.workers.UvicornWorker

# Run database migrations
uv run alembic upgrade head
uv run alembic downgrade -1
```

### Database
```bash
# Start PostgreSQL via Docker
docker-compose up -d

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Check database status
uv run alembic current
```

## Architecture

### Core Structure
- **Backend**: FastAPI application located in `backend/` directory
- **Database**: PostgreSQL with pgvector extension for vector operations
- **ORM**: SQLAlchemy with async support, using custom base classes for common fields
- **API**: RESTful API with v1 versioning under `backend/api/v1/`

### API Layer
- **Schemas**: Located in `backend/schemas/` directory for Pydantic models
- **Response Models**: Separate files for different modules (`admin.py`, `character.py`, `conversation.py`)
- **Common Patterns**: Base schemas for common responses (`PageResponse`, `ORMBase`, etc.)

### Key Components

#### Database Layer
- **Models**: Located in `backend/models/` with base classes in `backend/models/base.py`
- **CRUD**: Database operations in `backend/crud/` directory
- **Base Classes**:
  - `DbBase`: SQLAlchemy declarative base
  - `TableBase`: Base with ID field
  - `ORMBaseSmall`: Base with created_at timestamp
  - `ORMBase`: Full base with updated_at, deleted_at, and is_delete fields

#### Database Models
- **Admin**: User management (`User`)
- **Character**: Character, World, Label, Document models for role-playing system
- **Conversation**: LLM conversation session and message models (`ConversationSession`, `ConversationHistory`, `Session2Character`)

#### Application Factory
- **Main App**: `backend/__init__.py` contains `create_app()` function
- **Lifespan**: Database initialization/deinitialization handled via async context manager
- **Middleware**: Applied via `make_middlewares()` function

#### Dependencies
- **Database**: Async session management via `get_session()` context manager
- **Configuration**: Environment variables loaded from `.env` file

### Database Configuration
- Uses PostgreSQL with pgvector extension for vector embeddings
- Async SQLAlchemy with asyncpg driver
- Soft delete pattern with `is_delete` and `deleted_at` fields
- Automatic timestamp management via SQLAlchemy triggers

### LLM Integration
- Modelscope integration for large language model capabilities
- Vector search support via pgvector
- JSON repair functionality for malformed LLM responses

## Project Setup

1. Copy `.env.example` to `.env` and configure database settings
2. Run `uv sync` to install dependencies
3. Start PostgreSQL: `docker-compose up -d`
4. Run migrations: `uv run alembic upgrade head`
5. Start development server: `uv run uvicorn backend:app --reload`