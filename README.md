# FastDiscordDB Project

## Overview
FastDiscordDB is a FastAPI-powered application designed to handle the storage and retrieval of Discord chat exports into a PostgreSQL database. This project utilizes DiscordChatExporter to fetch chats and provides API endpoints for querying these chats by keyword or date range.

## Project Structure
```
/FastDiscordDB
│
├── app                     # Main application package
│   ├── __init__.py         # Initializes the Python package
│   ├── main.py             # Entry point to the FastAPI app, contains app configurations
│   ├── dependencies.py     # Dependency injection for database sessions and configurations
│   ├── models.py           # SQLAlchemy ORM models for your database schema
│   ├── schemas.py          # Pydantic models for data validation and serialization
│   ├── crud.py             # CRUD operations (database interaction logic)
│   ├── services            # Business logic and service layer
│   │   ├── __init__.py
│   │   ├── chat_exporter.py # Handles the logic for exporting chats using DiscordChatExporter
│   │   └── chat_queries.py  # Business logic for querying chat data
│   ├── api                 # API endpoints organized by functionality
│   │   ├── __init__.py
│   │   ├── chat.py         # Endpoints for chat operations and dynamic channel handling
│   │   └── search.py       # Endpoints for searching chats by keyword and date
│   └── core                # Core application components
│       ├── config.py       # Configuration settings (e.g., database URL, API keys)
│       ├── security.py     # Security and authentication functions
│       └── database.py     # Database connection setup
│
├── tests                   # Test modules
│   ├── __init__.py
│   ├── conftest.py         # Fixture configuration for tests
│   ├── test_main.py        # Tests for main app functionality
│   ├── test_database.py    # Tests involving database operations
│   └── test_api            # Tests for API endpoints
│       ├── __init__.py
│       ├── test_chat.py    # Tests for chat export and dynamic channel functionality
│       └── test_search.py  # Tests for search functionality
│
├── alembic                 # Database migrations managed by Alembic
│   ├── versions            # Individual migration scripts
│   └── env.py              # Alembic environment configuration
│
├── venv                    # Virtual environment directory (not committed to version control)
│
├── requirements.txt        # Project dependencies
├── .gitignore              # Specifies intentionally untracked files to ignore
└── README.md               # Project overview and setup instructions
```