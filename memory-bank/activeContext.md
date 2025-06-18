# Active Context: Database Synchronization Utility

## 1. Current Work Focus (as of 2025-06-18 10:51)

-   **Phase:** Feature Enhancement - Vehicle Search API.
-   **Activity:** Implemented fallback logic for `_inv` fields in `vehicle_search_api/app/main.py`.
    -   The API now prioritizes `marca_inv` and `modelo_inv` over `marca` and `modelo` respectively.
    -   If `_inv` fields are null or empty, the API uses the standard fields.
-   **Previous Activity (as of 2025-06-04 17:47):**
    -   Received request to build a FastAPI application with Docker to expose an endpoint for querying car data from Azure MySQL.
-   **Activity:**
    -   Received request to build a FastAPI application with Docker to expose an endpoint for querying car data from Azure MySQL.
    -   API key: `Q9iPw1UpAY5s8RKxZPZEwRMFVH6yqK9UzAHj3rvjqmDua9Fzf7UwumqGZTM5MA80loFSbdQFyrVoPgp9PuUKIjQrpjWurAz7kUXSNK47f6Api2ogfwwe5ZyU9TgiTiY6` (to be stored in `.env`).
    -   Identified `vehicles_stock` table schema by inspecting the local SQLite DB (`mysql_to_sqlite_sync/data/local_vehicles_stock.db`).
    -   Key queryable fields identified: `marca`, `modelo`, `color`, `tipo_transmision`, `kms`, `pvp_api`, `fecha_matriculacion` (for year), `vin`.
    -   Started updating Memory Bank files (`projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`) to reflect this new project component.
-   **Objective:** To create the FastAPI application, Dockerfile, `.env` file, and necessary supporting files for the vehicle search API.

## 2. Recent Changes & Decisions

-   **New Project Initiated:** Vehicle Search API.
-   **Technology Stack for API:** FastAPI, Docker, Python, SQLAlchemy, Uvicorn.
-   **Authentication Method:** API Key (`X-API-Key` header).
-   **Configuration Management for API:** `.env` file for API key and database credentials (passed as environment variables to Docker).
-   **Database Schema Source:** Leveraged existing local SQLite DB to infer schema for `vehicles_stock` on Azure.
-   **Implemented `_inv` Field Fallback (2025-06-18):** Modified `vehicle_search_api/app/main.py` to use `marca_inv` and `modelo_inv` as primary sources, falling back to `marca` and `modelo` if the `_inv` versions are empty or null.

## 3. Next Steps (Immediate)

1.  **Complete Memory Bank Update:**
    -   Update `activeContext.md` (this file).
    -   Update `progress.md` to reflect the start of the new API project and the status of the previous sync utility project.
2.  **Create Project Directory:** Create a new directory for the FastAPI project (e.g., `vehicle_search_api/`).
3.  **Create `.env` file:** Inside `vehicle_search_api/`, create `.env` with the provided API_KEY and placeholders for Azure DB credentials.
4.  **Create `requirements.txt`:** For the FastAPI application.
5.  **Develop FastAPI Application (`main.py`):**
    -   Implement API key authentication.
    -   Implement database connection logic for Azure MySQL (using credentials from env vars).
    -   Create the `/cars/` endpoint with query parameters for make, model, year, color, etc.
    -   Implement SQL query construction and execution.
    -   Define Pydantic models for request and response.
6.  **Create `Dockerfile`:** To containerize the FastAPI application.
7.  **Create `docker-compose.yml` (Optional but Recommended):** For easier local development and running.

## 4. Active Considerations & Questions

-   **Azure DB Credentials for API:** Will use the same credentials as in `mysql_to_sqlite_sync/config.ini` for `azure_mysql_db` (host, user, password, database name, ssl_mode). These will need to be set as environment variables for the Docker container.
-   **Specific query logic:** Keep the query simple as requested, focusing on direct matches for make, model, color, and potentially ranges for year/kms/price if straightforward.
-   **Error Handling in API:** Ensure robust error handling for DB connection issues, invalid API keys, and bad query parameters.

## 5. Important Patterns & Preferences (for new API)

-   **Secure by Default:** API key authentication is a primary requirement.
-   **Environment-Driven Configuration:** Align with Docker best practices.
-   **Simplicity in Endpoint Design:** Focus on common, straightforward query parameters.
-   **Leverage Existing Infrastructure:** Use the already populated Azure MySQL database.
-   **Clear Documentation (Memory Bank):** Continue detailed updates.
