# Tech Context: Database Synchronization Utility

## 1. Core Technologies

-   **Programming Language:** Python (version 3.7+ recommended).
-   **Command-Line Interface:** `argparse` module (Python standard library) for handling runtime arguments (e.g., target selection).
-   **Data Sources:**
    -   Primary: MySQL (external, self-hosted or cloud).
    -   Fallback: SQLite3 (local file-based).
-   **Data Targets:**
    -   SQLite3 (local file-based).
    -   Azure MySQL (cloud-hosted MySQL, requires SSL).
-   **Database Interaction:**
    -   `pandas` for reading from SQL and writing to SQL.
    -   `SQLAlchemy` as an abstraction layer used by pandas and for engine creation.
    -   `mysql-connector-python` as the specific connector for all MySQL communications (source and Azure target).

## 2. Development Setup

-   Python environment (e.g., venv, conda).
-   Installation of Python packages via `pip` from `requirements.txt`.
-   IDE or text editor.
-   Access to the primary external MySQL database and the target Azure MySQL database for testing.
-   SQLite client for inspecting the local database.

## 3. Technical Constraints & Considerations

-   **Database Credentials:** Secure handling remains crucial. `config.ini` stores them; consider environment variables for production.
-   **Azure MySQL Connectivity:**
    -   Requires SSL. `ssl_mode` is configured in `config.ini` (e.g., 'require').
    -   If Azure's default CA is not sufficient or if client certificates are used, `ssl_ca`, `ssl_cert`, `ssl_key` might be needed in `config.ini`.
    -   The database specified in `[azure_mysql_db]` (e.g., `vehicles_db`) must exist, or the user must have permissions to create it. The script handles table creation/replacement.
-   **Network Reliability:**
    -   The script now has a fallback mechanism: if the primary external MySQL source is unreachable, it can use the local SQLite DB as a source.
    -   Stable connection to the chosen *target* (SQLite or Azure MySQL) is still required during the write phase.
-   **Data Volume:** "Truncate-and-load" performance considerations remain for very large datasets.
-   **Schema Changes:** The script assumes the source schema (from primary external DB or fallback SQLite) is consistent for the target table.
-   **Python Version:** Compatibility with Python 3.7+ is targeted.

## 4. Key Dependencies (`requirements.txt`)

```
# Core data handling
pandas

# SQLAlchemy is used by pandas.to_sql for many database types and for engine creation
sqlalchemy

# MySQL connector for both primary source and Azure MySQL target
mysql-connector-python
```
(`argparse` is part of the Python standard library and does not need to be listed in `requirements.txt`.)

## 5. Tool Usage Patterns

-   **Configuration File (`config.ini`):**
    -   Centralized storage for all database connection strings (primary source, local SQLite, Azure MySQL).
    -   Stores source query, table names, SSL parameters for Azure.
    -   Contains general operational settings: `default_target`, `target_argument_enabled`, `fallback_to_local_source_on_failure`.
    -   Read using Python's `configparser` module.
-   **Command-Line Arguments:**
    -   `argparse` module used to process arguments like `--target` to override the default target database.
-   **Logging:** Python's built-in `logging` module configured for detailed operational feedback to console (and potentially a file, though not explicitly configured in script yet).
-   **Custom Exceptions:** `SourceConnectionError` used to manage control flow for source fallback.

## 6. Tech Context: Vehicle Search API (New as of 2025-06-04)

### 6.1. Core Technologies

-   **Programming Language:** Python (version 3.8+ for FastAPI features).
-   **API Framework:** FastAPI.
-   **Web Server (for FastAPI):** Uvicorn.
-   **Containerization:** Docker.
-   **Data Validation:** Pydantic (comes with FastAPI).
-   **Database:** Azure MySQL.
-   **Database Interaction:**
    -   `SQLAlchemy` (Core or ORM, potentially with `aiomysql` or `asyncmy` for async operations if chosen).
    -   `mysql-connector-python` (if using synchronous SQLAlchemy or direct connections).
-   **Environment Variable Management:** `python-dotenv` (for loading `.env` files).

### 6.2. Development Setup

-   Python environment (e.g., venv, conda).
-   Docker Desktop or Docker Engine/CLI.
-   Installation of Python packages (FastAPI, Uvicorn, SQLAlchemy, mysql-connector-python, python-dotenv, etc.) via `pip`.
-   IDE or text editor (e.g., VS Code with Docker and Python extensions).
-   Access to the Azure MySQL database (`vehicles_db`) for testing.
-   API testing tool (e.g., Postman, curl, or FastAPI's interactive docs).

### 6.3. Technical Constraints & Considerations

-   **API Key Security:** The API key must be kept secret. It will be stored in an `.env` file, loaded into the Docker container's environment.
-   **Database Credentials for API:**
    -   Similar to the sync utility, Azure MySQL credentials (host, user, password, dbname, SSL settings) need to be securely managed. These will be passed as environment variables to the Docker container.
    -   The `config.ini` from `mysql_to_sqlite_sync` contains these details and can serve as a reference for setting up environment variables for the API.
-   **Azure MySQL Connectivity:**
    -   SSL is required. The API's database connection logic must include SSL configuration (e.g., `ssl_mode='require'`).
-   **Docker Networking:** If the API needs to be accessible outside the local machine, Docker port mapping will be necessary (e.g., `-p 8000:80`).
-   **Scalability:** FastAPI with Uvicorn is highly performant. For further scalability, multiple Docker container instances could be run behind a load balancer.
-   **Schema for `vehicles_stock`:** The API will query based on the schema identified:
    -   `marca` (TEXT) - Make
    -   `modelo` (TEXT) - Model
    -   `color` (TEXT) - Color
    -   `tipo_transmision` (TEXT) - Transmission
    -   `kms` (FLOAT) - Kilometers
    -   `pvp_api` (FLOAT) - Price
    -   `fecha_matriculacion` (DATETIME) - For Year extraction
    -   `vin` (TEXT) - VIN

### 6.4. Key Dependencies (for the API - example `requirements.txt`)

```
fastapi
uvicorn[standard] # Includes standard JSON parsing and server features
sqlalchemy
mysql-connector-python # Or an async connector like aiomysql/asyncmy if going fully async
python-dotenv
pydantic # Usually comes with fastapi, but good to list
```

### 6.5. Tool Usage Patterns (API)

-   **`.env` File:** For storing `API_KEY` and database credentials during local development.
-   **Docker & Dockerfile:** To define the container image, including copying application code, installing dependencies, and setting the entry point (Uvicorn).
-   **FastAPI Interactive Docs:** (`/docs` and `/redoc`) for testing the API endpoint during development.
-   **Environment Variables in Docker:** For passing configuration (API key, DB credentials) to the running container.
