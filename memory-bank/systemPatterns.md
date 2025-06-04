# System Patterns: Database Synchronization Utility

## 1. System Architecture Overview

The system is a Python script performing an Extract, Load (EL) process. It supports multiple sources (primary external, fallback local) and multiple targets (local SQLite, Azure MySQL), configurable via a file and command-line arguments.

```mermaid
graph LR
    subgraph Sources
        A[Primary External DB View (MySQL)]
        C[Local SQLite DB (as Fallback Source)]
    end

    subgraph Targets
        E[Local SQLite DB (as Target)]
        F[Azure MySQL DB (as Target)]
    end

    B(Python Script);
    D[User];
    G[config.ini];
    H[CLI Arguments --target];

    D -- Runs --> B;
    H -- Influences --> B;
    G -- Configures --> B;

    A -- Read via Python DB Connector --> B;
    B -- Optionally Reads if A fails --> C;
    
    B -- Write via SQLite3/MySQL Connector --> E;
    B -- Write via MySQL Connector (SSL) --> F;

    D -- Queries --> E;
    D -- Queries --> F;
```

## 2. Key Technical Decisions

-   **Language:** Python 3.x.
-   **Data Sources:**
    -   Primary: External MySQL database (configurable).
    -   Fallback: Local SQLite database (configurable, used if primary source fails).
-   **Data Targets:**
    -   Local SQLite database.
    -   Azure MySQL database (configurable, includes SSL connection).
-   **Default Target:** Azure MySQL, configurable in `config.ini`.
-   **Target Selection:** Can be overridden via command-line argument (`--target`).
-   **External Database Connectivity:** `SQLAlchemy` and `mysql-connector-python` for MySQL connections. `sqlite3` (via SQLAlchemy/Pandas) for SQLite.
-   **Configuration Management:** `config.ini` file for all connection parameters, source query, target details, SSL settings, and operational flags (e.g., fallback enabling, default target).
-   **Data Handling:** Pandas DataFrames for internal data manipulation.
-   **SSL for Azure:** `ssl_mode` (e.g., 'require') configured for Azure MySQL connections.

## 3. Design Patterns

-   **Configuration-Driven:** Script behavior heavily driven by `config.ini`.
-   **Command-Line Overrides:** Specific configurations (like target DB) can be overridden at runtime.
-   **Modular Design:**
    -   Separate functions for:
        -   Configuration loading.
        -   Fetching from primary external DB.
        -   Fetching from fallback SQLite DB.
        -   Writing to local SQLite DB.
        -   Writing to Azure MySQL DB.
    -   Main orchestrator function manages the workflow, including source selection, fallback, and target dispatch.
-   **Error Handling:**
    -   Try-except blocks for database operations, file I/O.
    -   Custom `SourceConnectionError` to manage fallback logic.
    -   Comprehensive logging via Python's `logging` module.
-   **Fallback Mechanism:** If the primary data source is unavailable, the script can use a local SQLite database as an alternative source.
-   **Idempotency:** The "truncate-and-load" strategy for writing to targets ensures idempotency.

## 4. Data Synchronization Strategy

-   **Primary Strategy: Truncate-and-Load:**
    -   Applies to both local SQLite and Azure MySQL targets.
    -   Ensures the target table is an exact replica of the (chosen) source data at the time of sync.
    -   **Process:**
        1.  Fetch all data from the determined source (primary or fallback).
        2.  If the target table exists, it's effectively replaced with new data (Pandas `to_sql` with `if_exists='replace'` handles dropping/recreating or deleting rows and inserting).
        3.  Insert all fetched data into the target table.
-   **Alternative (Future Consideration): Upsert (Update or Insert):**
    -   Remains a future consideration if performance with truncate-and-load becomes an issue for very large datasets with minimal changes.

## 5. Logging and Feedback

-   Use Python's `logging` module.
-   Log key steps: script start/end, configuration loading, connection attempts (source/target), data fetching (source, number of rows), data loading (target, number of rows), fallback activation, errors encountered.
-   Provide clear messages to the console.

## 6. System Patterns: Vehicle Search API (New as of 2025-06-04)

### 6.1. System Architecture Overview

The API is a FastAPI application running inside a Docker container. It connects to an Azure MySQL database and exposes a secured endpoint for querying vehicle data.

```mermaid
graph TD
    subgraph Client
        AA[External System (e.g., OpenAI Tool)]
    end

    subgraph API_Service
        BB[Docker Container] --> CC{FastAPI App};
        CC -- Reads Env Vars --> DD[.env File / Env Vars (API_KEY, DB Config)];
        CC -- Uses SQLAlchemy & mysql-connector --> EE[Azure MySQL (vehicles_db - vehicles_stock table)];
    end

    AA -- HTTPS Request (GET /cars/) with API Key in Header --> CC;
    CC -- JSON Response --> AA;
```

### 6.2. Key Technical Decisions

-   **Framework:** FastAPI for its performance and ease of use, especially for Pydantic-based data validation.
-   **Containerization:** Docker for packaging and deployment.
-   **Database:** Azure MySQL (existing `vehicles_db`, `vehicles_stock` table).
-   **Database Connectivity:** `SQLAlchemy` (async variant if possible with FastAPI, or standard sync with `run_in_executor`) and `mysql-connector-python`.
-   **API Key Authentication:**
    -   API key stored in an `.env` file (loaded by Docker/FastAPI).
    -   Custom dependency in FastAPI to check for `X-API-Key` header.
-   **Configuration:**
    -   `.env` file for API_KEY.
    -   Database connection details (host, user, password, database, SSL settings) will be passed as environment variables to the Docker container. These can be sourced from a local `.env` file during development or set directly in the Docker run command/compose file for deployment.
-   **Data Handling:** Pydantic models for request query parameters and response models.

### 6.3. Design Patterns

-   **Dependency Injection (FastAPI):** Used for API key authentication and potentially database sessions.
-   **Environment-Based Configuration:** Critical settings (API key, DB credentials) managed via environment variables, suitable for Dockerized applications.
-   **Layered Architecture (Conceptual):**
    -   API Layer (FastAPI routing, request/response handling).
    -   Service/Business Logic Layer (query construction, data fetching logic).
    -   Data Access Layer (database connection, query execution).
-   **Asynchronous (Recommended for FastAPI):** Utilize `async/await` for I/O-bound operations like database queries to improve concurrency, if feasible with the chosen database driver and SQLAlchemy setup.

### 6.4. Data Query Strategy

-   **Dynamic Query Building:** Construct SQL `WHERE` clauses based on the provided optional query parameters (make, model, year, color, etc.).
-   **Parameterization:** Use parameterized queries to prevent SQL injection vulnerabilities.
-   **Selective Fields:** Select only necessary columns from `vehicles_stock` to optimize data transfer.

### 6.5. Logging and Feedback (API)

-   FastAPI's default logging, potentially enhanced with `uvicorn` logging settings.
-   Log API requests (without sensitive data), database query execution (potentially summarized), and errors.
-   Return meaningful HTTP status codes and JSON error responses.

### 6.6. `vehicles_stock` Table Schema (Identified from local SQLite DB)

```
CREATE TABLE vehicles_stock (
    ficha_id BIGINT,
    workflow_nombre TEXT,
    workflow_id BIGINT,
    workflow_estado TEXT,
    workflow_estado_id BIGINT,
    workflow_subestado TEXT,
    workflow_subestado_id BIGINT,
    modelo TEXT,                     -- Model
    origen_custom TEXT,
    descripcion TEXT,
    tipo_transmision TEXT,           -- Transmission Type
    matricula TEXT,
    vin TEXT,                        -- VIN
    fecha_matriculacion DATETIME,    -- Registration Date (for Year)
    "fecha_matriculacion_JAWA" DATETIME,
    kms_vehiculo FLOAT,
    kms FLOAT,                       -- Kilometers
    kms_manual TEXT,
    color TEXT,                      -- Color
    interior TEXT,
    color_interior TEXT,
    equipamiento TEXT,
    fiscalidad FLOAT,
    pvp TEXT,
    garantia TEXT,
    comercial TEXT,
    fecha_reserva TEXT,
    observaciones TEXT,
    color_registro TEXT,
    "fiscalidad_GO" TEXT,
    marca TEXT,                      -- Make
    color_api TEXT,                  -- Alternative Color
    interior_api TEXT,
    fiscalidad_api FLOAT,
    pvp_api FLOAT,                   -- Price
    precio_base_api FLOAT,
    origen TEXT,
    marca_inv TEXT,
    modelo_inv TEXT,
    version_inv TEXT,
    codigo_jato_inv TEXT,
    publicar_inv TEXT,
    fecha_publicado_inv TEXT,
    codigo_progresion TEXT,
    tipo_venta TEXT,
    clase_vehiculo TEXT,
    grossvalue FLOAT,
    ubicacion TEXT,
    fecha_factura_compra TEXT,
    vehicle_stock_id TEXT
);
```
Key fields for API query: `marca`, `modelo`, `color` (or `color_api`), `tipo_transmision`, `kms`, `pvp_api`, `fecha_matriculacion` (for year), `vin`.
