# Product Context: Database Synchronization Utility

## 1. Problem Statement

The user needs to perform frequent local queries on data that resides in an external database. Directly querying the external database multiple times a day for various local analyses can be inefficient, slow, or may put an unnecessary load on the source system. Furthermore, the user might not always have a stable or fast connection to the external database when they need to perform these local analyses.

## 2. Solution Overview

A Python utility will be developed to periodically extract data from a specific view in the external database and load it into a local SQLite database. This local database will serve as a readily accessible, fast-performing cache for the user's analytical queries.

## 3. How It Should Work

1.  **Configuration:** The user will configure the utility with connection details for the external database (e.g., type, host, port, username, password, database name) and the name of the specific view to be synchronized. The local SQLite database file path will also be configurable.
2.  **Execution:** The user will run the Python script.
3.  **Connection:** The script will connect to the external database.
4.  **Data Extraction:** It will query the specified view to fetch all relevant data.
5.  **Local Database Update:**
    *   If the local SQLite database or the target table doesn't exist, it will be created based on the schema of the fetched data.
    *   The script will then populate/update the local table with the data from the view. A common approach is to replace all existing data in the local table with the fresh data from the view (truncate-and-load), ensuring the local copy is a current snapshot. Other strategies (e.g., upsert) can be considered if partial updates are more appropriate and identifiable.
6.  **Completion:** The script will indicate successful completion or report any errors encountered.
7.  **Local Querying:** After synchronization, the user can connect to the local SQLite database using any SQLite-compatible tool to perform their queries quickly and efficiently.

## 4. User Experience Goals

-   **Simplicity:** The utility should be easy to configure and run.
-   **Reliability:** The synchronization process should be robust and handle common database connection or query issues gracefully.
-   **Speed (Local Queries):** The primary benefit is fast local querying once the data is synchronized. The synchronization process itself should be reasonably efficient.
-   **Transparency:** Clear feedback on the synchronization status (success, failure, number of records processed if feasible).

## 5. Product Context: Vehicle Search API (New as of 2025-06-04)

### 5.1. Problem Statement

An external system (e.g., an OpenAI tool) needs to query vehicle stock information in real-time based on typical search criteria (make, model, year, color, etc.). This requires a secure, fast, and reliable API endpoint.

### 5.2. Solution Overview

A FastAPI application will be developed and containerized using Docker. This application will expose an API endpoint that connects to the Azure MySQL database (`vehicles_db`, `vehicles_stock` table) to retrieve vehicle data. The API will be secured using an API key.

### 5.3. How It Should Work

1.  **Deployment:** The FastAPI application is run as a Docker container.
2.  **Configuration:**
    *   An `.env` file will store the API_KEY for authentication.
    *   Database connection details for Azure MySQL (host, port, user, password, database name, SSL settings) will also be managed, likely through environment variables passed to the Docker container (potentially sourced from a configuration similar to `config.ini` or directly as environment variables).
3.  **API Request:** The client (e.g., OpenAI tool) sends a GET request to the `/cars/` endpoint with query parameters (e.g., `?make=Toyota&model=Camry&year=2023`). The request must include a valid API key in the headers (e.g., `X-API-Key: <your_api_key>`).
4.  **Authentication:** The FastAPI application validates the provided API key against the one stored in its environment.
5.  **Database Query:** If authentication is successful, the application constructs an SQL query based on the provided parameters and executes it against the `vehicles_stock` table in the Azure MySQL database.
6.  **API Response:** The application returns the query results (e.g., a list of matching vehicles) as a JSON response. If authentication fails or an error occurs, an appropriate HTTP error response is returned.

### 5.4. User Experience Goals (for the API consumer)

-   **Ease of Use:** The API endpoint should be straightforward to use with clear query parameters.
-   **Performance:** Queries should be executed efficiently to provide quick responses for real-time interactions.
-   **Security:** The API key mechanism ensures that only authorized clients can access the data.
-   **Reliability:** The API should be stable and consistently available.
-   **Clarity:** API responses should be well-structured (JSON) and error messages should be informative.
